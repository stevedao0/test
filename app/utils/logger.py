from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class AppLogger:
    _instance: Optional[AppLogger] = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._logger is None:
            self._setup_logger()

    def _setup_logger(self):
        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"

        self._logger = logging.getLogger("contract_management")
        self._logger.setLevel(logging.INFO)

        if not self._logger.handlers:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.INFO)

            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)

            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            self._logger.addHandler(file_handler)
            self._logger.addHandler(console_handler)

    def info(self, message: str, **kwargs):
        extra_info = " - " + " | ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
        self._logger.info(f"{message}{extra_info}")

    def warning(self, message: str, **kwargs):
        extra_info = " - " + " | ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
        self._logger.warning(f"{message}{extra_info}")

    def error(self, message: str, **kwargs):
        extra_info = " - " + " | ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
        self._logger.error(f"{message}{extra_info}")

    def debug(self, message: str, **kwargs):
        extra_info = " - " + " | ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
        self._logger.debug(f"{message}{extra_info}")

    def log_contract_created(self, contract_no: str, user: Optional[str] = None):
        self.info(f"Contract created", contract_no=contract_no, user=user or "system")

    def log_contract_updated(self, contract_no: str, user: Optional[str] = None):
        self.info(f"Contract updated", contract_no=contract_no, user=user or "system")

    def log_contract_deleted(self, contract_no: str, user: Optional[str] = None):
        self.warning(f"Contract deleted", contract_no=contract_no, user=user or "system")

    def log_annex_created(self, contract_no: str, annex_no: str, user: Optional[str] = None):
        self.info(f"Annex created", contract_no=contract_no, annex_no=annex_no, user=user or "system")

    def log_works_imported(self, contract_no: str, count: int, user: Optional[str] = None):
        self.info(f"Works imported", contract_no=contract_no, count=count, user=user or "system")

    def log_backup_created(self, file_path: str):
        self.info(f"Backup created", file=file_path)

    def log_error_occurred(self, error: Exception, context: Optional[str] = None):
        error_msg = f"{type(error).__name__}: {str(error)}"
        if context:
            error_msg = f"{context} - {error_msg}"
        self.error(error_msg)


logger = AppLogger()
