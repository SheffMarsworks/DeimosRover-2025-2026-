"""Shared path helpers for Tapo camera tools."""

from pathlib import Path
import os
from typing import Optional


def _discover_repo_root(start: Optional[Path] = None) -> Optional[Path]:
    current = (start or Path(__file__).resolve()).resolve()
    for candidate in [current] + list(current.parents):
        if (candidate / ".git").exists() and (candidate / "src").exists():
            return candidate
    return None


def default_image_dir_candidate() -> Path:
    env_value = os.getenv("DEIMOS_TAPOCAM_IMAGE_DIR")
    if env_value:
        return Path(env_value).expanduser()

    repo_root = _discover_repo_root()
    if repo_root is not None:
        return repo_root / "data" / "tapocam_images"

    return Path.cwd() / "data" / "tapocam_images"


def default_output_dir_arg() -> str:
    return str(default_image_dir_candidate())


def resolve_image_dir(output_dir: Optional[str] = None) -> Path:
    if output_dir:
        target = Path(output_dir).expanduser()
    else:
        target = default_image_dir_candidate()

    target = target.resolve()
    target.mkdir(parents=True, exist_ok=True)
    return target

