from yoyo import step

steps = [

    step("""
        CREATE TABLE IF NOT EXISTS pipeline_state (
            state_key TEXT PRIMARY KEY,
            discovery_completed BOOLEAN NOT NULL DEFAULT FALSE,
            discovery_date DATE,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """),

    step("""
        ALTER TABLE pipeline_state
        ADD COLUMN IF NOT EXISTS discovery_date DATE
    """)
]
