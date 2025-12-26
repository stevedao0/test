from __future__ import annotations

import traceback
from typing import Callable, Optional
from fastapi import Request
from fastapi.responses import RedirectResponse, JSONResponse


class ErrorHandler:
    @staticmethod
    def handle_route_error(
        error: Exception,
        *,
        redirect_url: str,
        error_message: Optional[str] = None,
        include_trace: bool = False
    ) -> RedirectResponse:
        if include_trace:
            traceback.print_exc()

        message = error_message or str(error) or type(error).__name__
        return RedirectResponse(
            url=f"{redirect_url}?error={message}",
            status_code=303
        )

    @staticmethod
    def handle_api_error(
        error: Exception,
        *,
        status_code: int = 500,
        include_trace: bool = False
    ) -> JSONResponse:
        if include_trace:
            traceback.print_exc()

        error_msg = str(error) if str(error) else type(error).__name__
        return JSONResponse(
            {"success": False, "error": error_msg},
            status_code=status_code
        )

    @staticmethod
    def safe_execute(
        func: Callable,
        *,
        on_error: Optional[Callable] = None,
        default_return=None,
        log_errors: bool = True
    ):
        try:
            return func()
        except Exception as e:
            if log_errors:
                traceback.print_exc()
            if on_error:
                return on_error(e)
            return default_return


def format_validation_error(error: Exception) -> str:
    error_str = str(error)
    if "validation error" in error_str.lower():
        try:
            lines = error_str.split("\n")
            relevant = [line for line in lines if "field" in line.lower() or "value" in line.lower()]
            if relevant:
                return "; ".join(relevant[:3])
        except Exception:
            pass
    return error_str


def create_error_response(
    error: Exception,
    *,
    is_api: bool = False,
    redirect_url: Optional[str] = None,
    status_code: int = 500,
    include_trace: bool = True
):
    if include_trace:
        traceback.print_exc()

    if is_api:
        return ErrorHandler.handle_api_error(error, status_code=status_code)
    elif redirect_url:
        return ErrorHandler.handle_route_error(error, redirect_url=redirect_url)
    else:
        raise error
