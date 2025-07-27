#!/usr/bin/env python3
"""Verify that migrations match the current model definitions."""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from sqlalchemy import MetaData, Table
from app.db.models import Base


def compare_tables():
    """Compare expected tables with model definitions."""
    
    # Expected tables from our models
    expected_tables = {
        'users': [
            'id', 'email', 'username', 'hashed_password', 
            'is_active', 'is_verified', 'is_superuser',
            'last_login_at', 'deleted_at', 'created_at', 'updated_at'
        ],
        'refresh_tokens': [
            'id', 'user_id', 'token_hash', 'expires_at', 
            'revoked_at', 'created_at', 'updated_at'
        ],
        'login_attempts': [
            'id', 'email', 'user_id', 'ip_address', 'user_agent',
            'success', 'attempted_at', 'created_at', 'updated_at'
        ],
        'audit_logs': [
            'id', 'user_id', 'action', 'resource_type', 'resource_id',
            'ip_address', 'user_agent', 'request_data', 'response_status',
            'created_at', 'updated_at'
        ]
    }
    
    print("Verifying table structures...")
    print("=" * 80)
    
    all_good = True
    
    for table_name, expected_columns in expected_tables.items():
        if table_name not in Base.metadata.tables:
            print(f"❌ Table '{table_name}' is missing from models!")
            all_good = False
            continue
            
        table = Base.metadata.tables[table_name]
        actual_columns = set(column.name for column in table.columns)
        expected_columns_set = set(expected_columns)
        
        missing = expected_columns_set - actual_columns
        extra = actual_columns - expected_columns_set
        
        if missing or extra:
            print(f"\n❌ Table '{table_name}' has mismatched columns:")
            if missing:
                print(f"   Missing: {missing}")
            if extra:
                print(f"   Extra: {extra}")
            all_good = False
        else:
            print(f"✅ Table '{table_name}' has all expected columns")
    
    return all_good


def check_indexes():
    """Verify that all necessary indexes exist."""
    
    print("\n\nVerifying indexes...")
    print("=" * 80)
    
    required_indexes = {
        'users': ['email', 'username', 'is_active', 'deleted_at'],
        'refresh_tokens': ['token_hash', 'user_id', 'expires_at'],
        'login_attempts': ['email', 'ip_address', 'user_id', 'attempted_at'],
        'audit_logs': ['user_id', 'action', 'created_at', 'resource_type']
    }
    
    all_good = True
    
    for table_name, required_cols in required_indexes.items():
        table = Base.metadata.tables[table_name]
        
        # Get all indexed columns
        indexed_columns = set()
        for index in table.indexes:
            indexed_columns.update(col.name for col in index.columns)
        
        # Check if required columns are indexed
        missing_indexes = []
        for col in required_cols:
            if col not in indexed_columns:
                missing_indexes.append(col)
        
        if missing_indexes:
            print(f"❌ Table '{table_name}' missing indexes on: {missing_indexes}")
            all_good = False
        else:
            print(f"✅ Table '{table_name}' has all required indexes")
    
    return all_good


def check_foreign_keys():
    """Verify foreign key relationships."""
    
    print("\n\nVerifying foreign keys...")
    print("=" * 80)
    
    expected_fks = {
        'refresh_tokens': [('user_id', 'users.id', 'CASCADE')],
        'login_attempts': [('user_id', 'users.id', 'SET NULL')],
        'audit_logs': [('user_id', 'users.id', 'SET NULL')]
    }
    
    all_good = True
    
    for table_name, expected in expected_fks.items():
        table = Base.metadata.tables[table_name]
        
        for fk_col, ref, ondelete in expected:
            found = False
            for fk in table.foreign_keys:
                if fk.parent.name == fk_col:
                    ref_name = f"{fk.column.table.name}.{fk.column.name}"
                    if ref_name == ref:
                        if fk.ondelete == ondelete:
                            print(f"✅ {table_name}.{fk_col} -> {ref} (ON DELETE {ondelete})")
                            found = True
                        else:
                            print(f"❌ {table_name}.{fk_col} -> {ref} has wrong ondelete: {fk.ondelete} != {ondelete}")
                            all_good = False
                            found = True
                    break
            
            if not found:
                print(f"❌ Missing foreign key: {table_name}.{fk_col} -> {ref}")
                all_good = False
    
    return all_good


def main():
    """Run all verification checks."""
    print("Migration Verification Script")
    print("=" * 80)
    
    checks = [
        compare_tables(),
        check_indexes(),
        check_foreign_keys()
    ]
    
    if all(checks):
        print("\n\n✅ All migration checks passed!")
        print("\nThe migration file is ready to be applied.")
        print("\nNext steps:")
        print("1. Ensure PostgreSQL is running")
        print("2. Run: make migrate")
        print("3. Verify with: psql -U postgres -d fullstack_db -c '\\dt'")
    else:
        print("\n\n❌ Some checks failed!")
        print("\nPlease fix the issues before running migrations.")
        sys.exit(1)


if __name__ == "__main__":
    main()