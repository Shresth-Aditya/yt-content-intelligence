from yoyo import step

steps = [

    step("""
        ALTER TABLE dim_videos
        ADD COLUMN niche TEXT
    """)
]