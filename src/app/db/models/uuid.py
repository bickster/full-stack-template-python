"""Custom UUID type that works with both PostgreSQL and SQLite."""

import uuid
from typing import Any

from sqlalchemy import CHAR, Dialect, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PGUUID


class UUID(TypeDecorator[uuid.UUID]):
    """Platform-independent UUID type.

    Uses PostgreSQL's UUID type when available, otherwise uses
    CHAR(36), storing as stringified hex values.
    """

    impl = CHAR(36)
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> Any:
        """Load implementation based on dialect."""
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PGUUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value: Any, dialect: Dialect) -> Any:
        """Process value before saving to database."""
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return value
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            else:
                return str(uuid.UUID(value))

    def process_result_value(self, value: Any, dialect: Dialect) -> Any:
        """Process value when loading from database."""
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return value
        else:
            if isinstance(value, uuid.UUID):
                return value
            else:
                return uuid.UUID(value)
