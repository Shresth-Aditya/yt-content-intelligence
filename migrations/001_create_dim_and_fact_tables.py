from yoyo import step

steps = [

    step("""
        CREATE TABLE IF NOT EXISTS dim_channels (
            channel_id TEXT PRIMARY KEY,
            channel_name TEXT NOT NULL,
            description TEXT
        )
    """),

    step("""
        CREATE TABLE IF NOT EXISTS dim_videos (
            video_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            published_at TIMESTAMP NOT NULL,
            channel_id TEXT,
            FOREIGN KEY (channel_id)
                REFERENCES dim_channels(channel_id)
        )
    """),

    step("""
        CREATE TABLE IF NOT EXISTS fact_video_daily_metrics (
            video_id TEXT,
            views BIGINT NOT NULL,
            likes BIGINT NOT NULL,
            comments BIGINT NOT NULL,
            snapshot_date DATE NOT NULL,

            PRIMARY KEY (video_id, snapshot_date),

            FOREIGN KEY (video_id)
                REFERENCES dim_videos(video_id)
        )
    """)
]