from yoyo import step

steps = [

    step("""
        CREATE TABLE IF NOT EXISTS bronze_youtube_api_responses (
            bronze_id BIGSERIAL PRIMARY KEY,
            run_id BIGINT,
            source_system TEXT NOT NULL DEFAULT 'youtube',
            endpoint TEXT NOT NULL,
            request_params JSONB,
            response_body JSONB NOT NULL,
            snapshot_date DATE,
            snapshot_time TIMESTAMP,
            fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            response_item_count INTEGER,
            response_hash TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """),

]
