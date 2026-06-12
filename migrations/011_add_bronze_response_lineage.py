from yoyo import step

steps = [

    step("""
        ALTER TABLE dim_channels
        ADD COLUMN source_bronze_id BIGINT,
        ADD CONSTRAINT fk_dim_channels_source_bronze
            FOREIGN KEY (source_bronze_id)
            REFERENCES bronze_youtube_api_responses(bronze_id);
    """),

    step("""
        ALTER TABLE dim_videos
        ADD COLUMN source_bronze_id BIGINT,
        ADD CONSTRAINT fk_dim_videos_source_bronze
            FOREIGN KEY (source_bronze_id)
            REFERENCES bronze_youtube_api_responses(bronze_id);
    """),

    step("""
        ALTER TABLE fact_video_snapshots
        ADD COLUMN source_bronze_id BIGINT,
        ADD CONSTRAINT fk_fact_video_snapshots_source_bronze
            FOREIGN KEY (source_bronze_id)
            REFERENCES bronze_youtube_api_responses(bronze_id);
    """)
]
