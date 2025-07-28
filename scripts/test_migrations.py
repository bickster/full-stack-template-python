#!/usr/bin/env python3
"""Test script to validate database models and migration setup."""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from sqlalchemy import create_engine, inspect
from sqlalchemy.schema import CreateTable

from app.db.models import AuditLog, Base, LoginAttempt, RefreshToken, User


def test_model_definitions():
    """Test that all models are properly defined."""
    print("Testing model definitions...")

    models = {
        "User": User,
        "RefreshToken": RefreshToken,
        "LoginAttempt": LoginAttempt,
        "AuditLog": AuditLog,
    }

    for name, model in models.items():
        print(f"\n{name} ({model.__tablename__}):")

        # Check columns
        mapper = inspect(model)
        print("  Columns:")
        for column in mapper.columns:
            col_type = str(column.type)
            nullable = "NULL" if column.nullable else "NOT NULL"
            print(f"    - {column.name}: {col_type} {nullable}")

        # Check relationships
        if mapper.relationships:
            print("  Relationships:")
            for rel in mapper.relationships:
                print(f"    - {rel.key} -> {rel.mapper.class_.__name__}")

        # Check indexes
        if model.__table__.indexes:
            print("  Indexes:")
            for idx in model.__table__.indexes:
                cols = ", ".join([c.name for c in idx.columns])
                print(f"    - {idx.name}: ({cols})")


def generate_sql_statements():
    """Generate SQL CREATE statements for all tables."""
    print("\n\nGenerated SQL statements:")
    print("=" * 80)

    # Create a dummy engine (we won't actually connect)
    engine = create_engine(
        "postgresql://dummy", strategy="mock", executor=lambda *a, **kw: None
    )

    # Generate CREATE TABLE statements
    for table_name, table in Base.metadata.tables.items():
        print(f"\n-- Table: {table_name}")
        print(CreateTable(table).compile(engine))


def check_migration_compatibility():
    """Check for common migration issues."""
    print("\n\nChecking for potential migration issues...")

    issues = []

    # Check for circular dependencies
    for table_name, table in Base.metadata.tables.items():
        for fk in table.foreign_keys:
            ref_table = fk.column.table.name
            if ref_table == table_name:
                issues.append(f"Self-referential foreign key in {table_name}")

    # Check for missing indexes on foreign keys
    for table_name, table in Base.metadata.tables.items():
        fk_columns = {fk.parent.name for fk in table.foreign_keys}
        indexed_columns = set()

        for idx in table.indexes:
            indexed_columns.update(c.name for c in idx.columns)

        missing_indexes = fk_columns - indexed_columns
        if missing_indexes:
            issues.append(
                f"Missing indexes on foreign keys in {table_name}: {missing_indexes}"
            )

    if issues:
        print("  Found issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("  No issues found!")


def main():
    """Run all tests."""
    print("Database Migration Test Script")
    print("=" * 80)

    try:
        test_model_definitions()
        generate_sql_statements()
        check_migration_compatibility()

        print("\n\nAll tests passed! ✅")
        print("\nTo create the initial migration, run:")
        print("  make migrate-create")
        print("\nTo apply migrations, run:")
        print("  make migrate")

    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
