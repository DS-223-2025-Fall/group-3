"""
Comprehensive script to verify all database tables exist and are populated.
"""

from sqlalchemy import text, inspect
from Database.database import engine

# All expected tables from the system
EXPECTED_TABLES = {
    # Core entity tables
    "locations": "Core entity",
    "students": "Core entity",
    "users": "Core entity",
    "instructors": "Core entity",
    "departments": "Core entity",
    "programs": "Core entity",
    "courses": "Core entity",
    "time_slots": "Core entity",
    "sections": "Core entity",
    "section_name": "Core entity",
    
    # Relationship/junction tables
    "prerequisites": "Junction table",
    "takes": "Junction table",
    "works": "Junction table",
    "hascourse": "Junction table",
    "preferred": "Junction table",
    
    # Cluster tables
    "clusters": "Cluster entity",
    "course_cluster": "Junction table",
    
    # User-generated tables (may be empty)
    "draft_schedules": "User-generated (optional)",
    "draft_schedule_sections": "User-generated (optional)",
    "recommendation_results": "User-generated (optional)",
}

# Tables that are allowed to be empty
OPTIONAL_TABLES = {
    "draft_schedules",
    "draft_schedule_sections",
    "recommendation_results"
}


def verify_all_tables():
    """
    Verify that all expected tables exist and are populated.
    """
    print("=" * 80)
    print("COMPREHENSIVE DATABASE TABLE VERIFICATION")
    print("=" * 80)
    print()
    
    try:
        with engine.connect() as connection:
            # Get all tables
            inspector = inspect(engine)
            all_tables = set(inspector.get_table_names())
            
            print("📊 TABLE STATUS REPORT")
            print("-" * 80)
            
            issues = []
            warnings = []
            total_rows = 0
            tables_found = 0
            tables_with_data = 0
            
            # Check each expected table
            for table_name, table_type in sorted(EXPECTED_TABLES.items()):
                table_lower = table_name.lower()
                
                # Check if table exists
                table_exists = any(t.lower() == table_lower for t in all_tables)
                
                if not table_exists:
                    print(f"❌ {table_name:30s} [{table_type:20s}] - TABLE MISSING")
                    issues.append(f"Table '{table_name}' does not exist")
                    continue
                
                tables_found += 1
                
                # Get actual table name (case-sensitive)
                actual_table = next(t for t in all_tables if t.lower() == table_lower)
                
                # Count rows
                result = connection.execute(text(f'SELECT COUNT(*) FROM "{actual_table}"'))
                row_count = result.scalar()
                total_rows += row_count
                
                # Check status
                if row_count == 0:
                    if table_name in OPTIONAL_TABLES:
                        status = "✓  EMPTY (OK)"
                    else:
                        status = "⚠️  EMPTY"
                        warnings.append(f"Table '{table_name}' is empty (expected to have data)")
                else:
                    status = "✓  OK"
                    tables_with_data += 1
                
                print(f"{status:12s} {table_name:30s} [{table_type:20s}] - {row_count:6d} rows")
            
            # Check for unexpected tables
            expected_table_names = {t.lower() for t in EXPECTED_TABLES.keys()}
            unexpected_tables = [
                t for t in all_tables 
                if t.lower() not in expected_table_names 
                and not t.lower().startswith('alembic')  # Ignore migration tables
            ]
            
            if unexpected_tables:
                print()
                print("-" * 80)
                print("📋 UNEXPECTED TABLES (not in expected list):")
                print("-" * 80)
                for table in sorted(unexpected_tables):
                    result = connection.execute(text(f'SELECT COUNT(*) FROM "{table}"'))
                    row_count = result.scalar()
                    print(f"   {table:30s} - {row_count:6d} rows")
            
            # Summary
            print()
            print("=" * 80)
            print("SUMMARY")
            print("=" * 80)
            print(f"Expected tables:        {len(EXPECTED_TABLES)}")
            print(f"Tables found:           {tables_found}")
            print(f"Tables with data:       {tables_with_data}")
            print(f"Total rows:             {total_rows:,}")
            print()
            
            if issues:
                print(f"❌ CRITICAL ISSUES ({len(issues)}):")
                for issue in issues:
                    print(f"   - {issue}")
                print()
            
            if warnings:
                print(f"⚠️  WARNINGS ({len(warnings)}):")
                for warning in warnings:
                    print(f"   - {warning}")
                print()
            
            if not issues and not warnings:
                print("✅ All tables are healthy and properly populated!")
                return True
            elif not issues:
                print("⚠️  Some tables are empty, but this may be expected for optional tables.")
                return True
            else:
                print("❌ Critical issues found. Please review the errors above.")
                return False
                
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = verify_all_tables()
    exit(0 if success else 1)

