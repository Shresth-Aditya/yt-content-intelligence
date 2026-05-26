from yoyo import step

steps = [

    step("""
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            id SERIAL PRIMARY KEY,
            execution_time_seconds DOUBLE PRECISION,
            videos_processed INTEGER,
            status VARCHAR(20),
            run_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )
    """)
]