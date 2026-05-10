import os
import uuid
import psycopg2
from dotenv import load_dotenv

load_dotenv()

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL"
)

def test_database_integration():

    conn = psycopg2.connect(
        TEST_DATABASE_URL
    )

    try:

        cursor = conn.cursor()
        # ---------------------------------
        # Unique temporary table name
        # ---------------------------------
        table_name = (
            f"test_table_{uuid.uuid4().hex[:8]}"
        )
        # ---------------------------------
        # 1. Create table
        # ---------------------------------

        cursor.execute(f"""
            CREATE TABLE {table_name} (

                id SERIAL PRIMARY KEY,
                name TEXT
            )
        """)

        # ---------------------------------
        # 2. Verify table exists
        # ---------------------------------

        cursor.execute(f"""
            SELECT *
            FROM {table_name}
        """)

        rows = cursor.fetchall()

        assert rows == []

        # ---------------------------------
        # 3. Insert sample data
        # ---------------------------------

        expected_name = "Shresth"

        cursor.execute(f"""
            INSERT INTO {table_name} (name)
            VALUES (%s)
        """, (expected_name,))

        # ---------------------------------
        # 4. Select inserted data
        # ---------------------------------

        cursor.execute(f"""
            SELECT name
            FROM {table_name}
        """)

        rows = cursor.fetchall()

        # ---------------------------------
        # 5. Validate data
        # ---------------------------------

        assert len(rows) == 1

        assert rows[0][0] == expected_name

        # ---------------------------------
        # 6. Rollback transaction
        # ---------------------------------

        conn.rollback()

    finally:

        conn.close()