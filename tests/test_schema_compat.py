from sqlalchemy import create_engine, inspect, text

from app.core.schema_compat import ensure_schema_compatibility


def test_schema_compat_adds_missing_growth_columns_to_users_table():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE users (
                  id INTEGER PRIMARY KEY,
                  name VARCHAR(120) NOT NULL,
                  email VARCHAR(255) NOT NULL UNIQUE,
                  password_hash VARCHAR(255) NOT NULL
                )
                """
            )
        )

    ensure_schema_compatibility(engine)

    inspector = inspect(engine)
    columns = {column["name"] for column in inspector.get_columns("users")}
    assert "current_streak" in columns
    assert "longest_streak" in columns
    assert "last_active_date" in columns
    assert "referral_code" in columns
    assert "referred_by_user_id" in columns
    assert "referred_count" in columns
    assert "daily_mission_progress" in inspector.get_table_names()
    assert "analytics_events" in inspector.get_table_names()
