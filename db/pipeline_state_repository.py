from db.connection import get_connection, release_connection

DISCOVERY_STATE_KEY = "daily_discovery"


def has_discovery_run_for_date(snapshot_date):

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT discovery_completed
                FROM pipeline_state
                WHERE state_key = %s
                    AND discovery_date = %s::date
            """, (
                DISCOVERY_STATE_KEY,
                snapshot_date
            ))

            row = cursor.fetchone()

        if row is None:
            return False

        return row[0] is True

    finally:
        release_connection(conn)


def mark_discovery_run_for_date(snapshot_date):

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO pipeline_state (
                    state_key,
                    discovery_completed,
                    discovery_date,
                    updated_at
                )
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (state_key)
                DO UPDATE SET
                    discovery_completed = EXCLUDED.discovery_completed,
                    discovery_date = EXCLUDED.discovery_date,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                DISCOVERY_STATE_KEY,
                True,
                snapshot_date
            ))

        conn.commit()

    finally:
        release_connection(conn)
