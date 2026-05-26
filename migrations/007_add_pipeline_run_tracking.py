from yoyo import step

steps = [

    step("""
        ALTER TABLE pipeline_runs
        RENAME COLUMN id TO run_id
    """),

    step("""
        ALTER TABLE dim_channels
        ADD COLUMN run_id INTEGER,
        ADD CONSTRAINT fk_dim_channels_run
            FOREIGN KEY (run_id)
            REFERENCES pipeline_runs(run_id)
    """),

    step("""
        ALTER TABLE dim_videos
        ADD COLUMN run_id INTEGER,
        ADD CONSTRAINT fk_dim_videos_run
            FOREIGN KEY (run_id)
            REFERENCES pipeline_runs(run_id)
    """),

    step("""
        ALTER TABLE fact_video_daily_metrics
        ADD COLUMN run_id INTEGER,
        ADD CONSTRAINT fk_fact_video_daily_metrics_run
            FOREIGN KEY (run_id)
            REFERENCES pipeline_runs(run_id)
    """)
]