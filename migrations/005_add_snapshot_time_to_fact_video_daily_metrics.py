from yoyo import step

steps = [
    step("""
        ALTER TABLE fact_video_daily_metrics
        ADD COLUMN snapshot_time TIMESTAMP
    """),

    step("""
        UPDATE fact_video_daily_metrics
        SET snapshot_time = CURRENT_TIMESTAMP
        WHERE snapshot_time IS NULL
    """),

    step("""
        ALTER TABLE fact_video_daily_metrics
        ALTER COLUMN snapshot_time SET NOT NULL
    """)
]