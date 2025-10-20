from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


@dataclass
class Result(Generic[T]):
    success: bool
    message: Optional[str] = None
    data: Optional[T] = None

    @staticmethod
    def ok(data: Optional[T] = None, message: Optional[str] = "OK") -> "Result[T]":
        return Result(success=True, message=message, data=data)

    @staticmethod
    def error(message: str) -> "Result[T]":
        return Result(success=False, message=message, data=None)