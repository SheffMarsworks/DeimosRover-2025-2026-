#!/usr/bin/env python3
"""
Waveshare USB-CAN-A <-> vcan0 SocketCAN bridge.
Usage: sudo python3 waveshare_can_bridge.py
"""
import serial, socket, struct, threading, sys, time

SERIAL_PORT = "/dev/ttyUSB0"
SERIAL_BAUD = 2000000
VCAN_IFACE  = "vcan0"

CANFRAME_FMT  = "=IB3x8s"
CANFRAME_SIZE = struct.calcsize(CANFRAME_FMT)
CAN_EFF_FLAG  = 0x80000000

def parse_waveshare(buf):
    if len(buf) < 4 or buf[0] != 0xAA: return None
    tb = buf[1]; ext = bool(tb & 0x20); dlc = tb & 0x0F
    needed = (1+1+4+dlc+1) if ext else (1+1+2+dlc+1)
    if len(buf) < needed or buf[needed-1] != 0x55: return None
    if ext:
        can_id = buf[2]|(buf[3]<<8)|(buf[4]<<16)|(buf[5]<<24)
        data = bytes(buf[6:6+dlc])
    else:
        can_id = buf[2]|(buf[3]<<8)
        data = bytes(buf[4:4+dlc])
    return (can_id, data, ext)

def build_waveshare(can_id, data, ext=True):
    dlc = len(data)
    tb = (dlc & 0x0F) | 0xC0 | (0x20 if ext else 0x00)
    frame = bytearray([0xAA, tb])
    frame += can_id.to_bytes(4 if ext else 2, 'little')
    frame.extend(data); frame.append(0x55)
    return bytes(frame)

def serial_to_vcan(ser, sock, stop):
    buf = bytearray()
    print("[bridge] serial->vcan started")
    while not stop.is_set():
        try: b = ser.read(1)
        except Exception as e: print(f"[bridge] serial read error: {e}"); stop.set(); break
        if not b: continue
        if len(buf) == 0 and b[0] != 0xAA: continue
        buf.extend(b)
        if len(buf) < 2: continue
        tb = buf[1]; ext = bool(tb & 0x20); dlc = tb & 0x0F
        needed = (1+1+4+dlc+1) if ext else (1+1+2+dlc+1)
        if len(buf) < needed: continue
        result = parse_waveshare(buf[:needed]); buf = buf[needed:]
        if result is None: continue
        can_id, data, is_ext = result
        raw_id = (can_id | CAN_EFF_FLAG) if is_ext else can_id
        try: sock.send(struct.pack(CANFRAME_FMT, raw_id, len(data), data.ljust(8, b'\x00')))
        except Exception as e: print(f"[bridge] vcan send error: {e}")

def vcan_to_serial(ser, sock, stop):
    print("[bridge] vcan->serial started")
    while not stop.is_set():
        try: raw = sock.recv(CANFRAME_SIZE)
        except Exception as e: print(f"[bridge] vcan recv error: {e}"); stop.set(); break
        if len(raw) < CANFRAME_SIZE: continue
        raw_id, dlc, data_padded = struct.unpack(CANFRAME_FMT, raw)
        is_ext = bool(raw_id & CAN_EFF_FLAG)
        can_id = raw_id & ~CAN_EFF_FLAG
        try: ser.write(build_waveshare(can_id, data_padded[:dlc], is_ext)); ser.flush()
        except Exception as e: print(f"[bridge] serial write error: {e}")

def main():
    print(f"[bridge] Opening {SERIAL_PORT} at {SERIAL_BAUD} baud...")
    try: ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=0.05)
    except Exception as e: print(f"[bridge] Serial error: {e}"); sys.exit(1)
    ser.reset_input_buffer()
    print(f"[bridge] Opening SocketCAN on {VCAN_IFACE}...")
    try:
        sock = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
        sock.bind((VCAN_IFACE,))
    except Exception as e:
        print(f"[bridge] vcan error: {e}"); ser.close(); sys.exit(1)
    stop = threading.Event()
    threading.Thread(target=serial_to_vcan, args=(ser,sock,stop), daemon=True).start()
    threading.Thread(target=vcan_to_serial, args=(ser,sock,stop), daemon=True).start()
    print("[bridge] Running. Ctrl+C to stop.")
    print("[bridge] Use can_interface: vcan0 in your ros2_control config")
    try:
        while not stop.is_set(): time.sleep(0.5)
    except KeyboardInterrupt: print("\n[bridge] Stopping...")
    finally: stop.set(); sock.close(); ser.close()

if __name__ == "__main__": main()
