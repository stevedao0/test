from __future__ import annotations

import json
import shutil
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any


def _ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


@contextmanager
def file_lock(lock_path: Path, *, timeout_seconds: float = 15.0, poll_seconds: float = 0.1):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    start = time.time()
    fh = None
    while True:
        try:
            # Exclusive create: fails if already exists
            fh = lock_path.open("x", encoding="utf-8")
            fh.write(datetime.now().isoformat(timespec="seconds"))
            fh.flush()
            break
        except FileExistsError:
            if time.time() - start >= timeout_seconds:
                raise TimeoutError(f"Timeout acquiring lock: {lock_path}")
            time.sleep(poll_seconds)

    try:
        yield
    finally:
        try:
            if fh:
                fh.close()
        finally:
            try:
                lock_path.unlink(missing_ok=True)
            except Exception:
                pass


def backup_file(path: Path, *, backup_dir: Path) -> Path | None:
    if not path.exists():
        return None

    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{path.stem}_{_ts()}{path.suffix}"
    shutil.copyfile(path, backup_path)
    return backup_path


def safe_replace_bytes(path: Path, data: bytes, *, backup_dir: Path | None = None) -> Path | None:
    if backup_dir is not None:
        backup_file(path, backup_dir=backup_dir)

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp_{_ts()}")
    tmp.write_bytes(data)
    tmp.replace(path)
    return path


def safe_move_to_backup(path: Path, *, backup_dir: Path) -> Path | None:
    if not path.exists():
        return None

    backup_dir.mkdir(parents=True, exist_ok=True)
    target = backup_dir / f"{path.stem}_{_ts()}{path.suffix}"
    try:
        path.replace(target)
    except Exception:
        shutil.copyfile(path, target)
        try:
            path.unlink()
        except Exception:
            pass
    return target


def audit_log(*, log_dir: Path, event: dict[str, Any]) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    event = dict(event)
    event.setdefault("ts", datetime.now().isoformat(timespec="seconds"))
    out_path = log_dir / f"audit_{datetime.now().strftime('%Y%m')}.jsonl"
    with out_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
