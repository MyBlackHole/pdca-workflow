from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RuntimeContractError(Exception):
    """A stable, machine-readable fail-closed runtime rejection."""

    code: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}
