from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional


class BackupManager:
    def __init__(self, storage_dir: Path, backup_dir: Optional[Path] = None):
        self.storage_dir = storage_dir
        self.backup_dir = backup_dir or (storage_dir.parent / "backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, file_path: Path) -> Path:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(file_path, backup_path)
        return backup_path

    def create_auto_backup(self, file_path: Path) -> Optional[Path]:
        try:
            if file_path.exists():
                return self.create_backup(file_path)
        except Exception:
            pass
        return None

    def list_backups(self, pattern: str = "*") -> list[Path]:
        return sorted(
            self.backup_dir.glob(pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

    def restore_backup(self, backup_path: Path, target_path: Path) -> None:
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")

        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup_path, target_path)

    def cleanup_old_backups(self, keep_count: int = 10, pattern: str = "*") -> int:
        backups = self.list_backups(pattern)
        removed_count = 0

        for backup in backups[keep_count:]:
            try:
                backup.unlink()
                removed_count += 1
            except Exception:
                pass

        return removed_count

    def get_backup_info(self, backup_path: Path) -> dict:
        if not backup_path.exists():
            return {}

        stat = backup_path.stat()
        return {
            "name": backup_path.name,
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime),
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "path": str(backup_path),
        }
