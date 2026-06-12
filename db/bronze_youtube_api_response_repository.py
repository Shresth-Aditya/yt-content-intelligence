import hashlib
import json

from psycopg2.extras import Json

from db.connection import get_connection, release_connection


def build_response_hash(response_body):
    encoded_response = json.dumps(
        response_body,
        sort_keys=True,
        separators=(",", ":")
    ).encode("utf-8")

    return hashlib.sha256(encoded_response).hexdigest()


def insert_bronze_youtube_api_response(
    api_response,
    run_id,
    snapshot_date,
    snapshot_time
):
    response_body = api_response["response_body"]
    response_hash = build_response_hash(response_body)

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO bronze_youtube_api_responses (
                    run_id,
                    endpoint,
                    request_params,
                    response_body,
                    snapshot_date,
                    snapshot_time,
                    response_item_count,
                    response_hash
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING bronze_id
            """, (
                run_id,
                api_response["endpoint"],
                Json(api_response["request_params"]),
                Json(response_body),
                snapshot_date,
                snapshot_time,
                len(response_body["items"]),
                response_hash
            ))

            bronze_id = cursor.fetchone()[0]

        conn.commit()
        return bronze_id

    finally:
        release_connection(conn)
