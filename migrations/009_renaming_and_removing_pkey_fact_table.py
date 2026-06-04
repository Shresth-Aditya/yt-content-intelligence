from yoyo import step

steps = [
    step(
        """
        ALTER TABLE fact_video_daily_metrics
        DROP CONSTRAINT fact_video_daily_metrics_pkey;

        ALTER TABLE fact_video_daily_metrics
        RENAME TO fact_video_snapshots;
        """
    )
]