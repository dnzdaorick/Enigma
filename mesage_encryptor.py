"""Message model wrapper for cryptographic operations."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Message:
    """Represents a text message with associated cryptographic key and image metadata."""

    message: str
    key: Optional[dict[str, str]] = None
    image_code: Optional[str] = None
    operation: str = "plain"

    def __len__(self) -> int:
        return len(self.message)

    def __str__(self) -> str:
        return self.message