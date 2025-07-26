"""Token storage implementations."""

import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from .types import AuthTokens


class TokenStorage(ABC):
    """Abstract base class for token storage."""

    @abstractmethod
    def get_access_token(self) -> Optional[str]:
        """Get stored access token."""
        pass

    @abstractmethod
    def get_refresh_token(self) -> Optional[str]:
        """Get stored refresh token."""
        pass

    @abstractmethod
    def set_tokens(self, tokens: AuthTokens) -> None:
        """Store tokens."""
        pass

    @abstractmethod
    def clear_tokens(self) -> None:
        """Clear stored tokens."""
        pass


class MemoryTokenStorage(TokenStorage):
    """In-memory token storage."""

    def __init__(self):
        """Initialize storage."""
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None

    def get_access_token(self) -> Optional[str]:
        """Get stored access token."""
        return self._access_token

    def get_refresh_token(self) -> Optional[str]:
        """Get stored refresh token."""
        return self._refresh_token

    def set_tokens(self, tokens: AuthTokens) -> None:
        """Store tokens."""
        self._access_token = tokens.access_token
        self._refresh_token = tokens.refresh_token

    def clear_tokens(self) -> None:
        """Clear stored tokens."""
        self._access_token = None
        self._refresh_token = None


class FileTokenStorage(TokenStorage):
    """File-based token storage."""

    def __init__(self, file_path: Optional[str] = None):
        """Initialize storage.
        
        Args:
            file_path: Path to token file. Defaults to ~/.fullstack/tokens.json
        """
        if file_path is None:
            home = Path.home()
            self.file_path = home / ".fullstack" / "tokens.json"
        else:
            self.file_path = Path(file_path)
        
        # Create directory if it doesn't exist
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def _read_tokens(self) -> dict:
        """Read tokens from file."""
        if not self.file_path.exists():
            return {}
        
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def _write_tokens(self, tokens: dict) -> None:
        """Write tokens to file."""
        with open(self.file_path, "w") as f:
            json.dump(tokens, f)
        
        # Set restrictive permissions (owner read/write only)
        os.chmod(self.file_path, 0o600)

    def get_access_token(self) -> Optional[str]:
        """Get stored access token."""
        tokens = self._read_tokens()
        return tokens.get("access_token")

    def get_refresh_token(self) -> Optional[str]:
        """Get stored refresh token."""
        tokens = self._read_tokens()
        return tokens.get("refresh_token")

    def set_tokens(self, tokens: AuthTokens) -> None:
        """Store tokens."""
        self._write_tokens({
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "token_type": tokens.token_type,
        })

    def clear_tokens(self) -> None:
        """Clear stored tokens."""
        if self.file_path.exists():
            self.file_path.unlink()