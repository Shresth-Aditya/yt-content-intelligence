from db.connection import get_connection, release_connection


def start_pipeline_run():

    conn = get_connection()

    try:
        with conn.cursor() as cursor:

            cursor.execute("""
                INSERT INTO pipeline_runs (
                    status
                )
                VALUES (%s)
                RETURNING run_id, run_date
            """, (
                "running",
            ))

            run_id, run_date = cursor.fetchone()

        conn.commit()
        return run_id, run_date

    finally:
        release_connection(conn)


def finish_pipeline_run(
    run_id,
    execution_time_seconds,
    videos_processed,
    status
):

    conn = get_connection()

    try:
        with conn.cursor() as cursor:

            cursor.execute("""
                UPDATE pipeline_runs
                SET
                    execution_time_seconds = %s,
                    videos_processed = %s,
                    status = %s
                WHERE run_id = %s
                RETURNING run_date
            """, (
                execution_time_seconds,
                videos_processed,
                status,
                run_id
            ))

            row = cursor.fetchone()

        conn.commit()

        if row is None:
            raise ValueError(f"Pipeline run {run_id} does not exist")

        return row[0]

    finally:
        release_connection(conn)


def insert_pipeline_run(
    execution_time_seconds,
    videos_processed,
    status
):

    conn = get_connection()

    try:
        with conn.cursor() as cursor:

            cursor.execute("""
                INSERT INTO pipeline_runs (
                    execution_time_seconds,
                    videos_processed,
                    status
                )
                VALUES (%s, %s, %s)
                RETURNING run_id, run_date
            """, (
                execution_time_seconds,
                videos_processed,
                status
            ))

            run_id, run_date = cursor.fetchone()

        conn.commit()
        return run_id, run_date

    finally:
        release_connection(conn)
