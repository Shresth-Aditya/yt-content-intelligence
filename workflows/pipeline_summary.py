def write_markdown_summary(metrics):

    summary = f"""# Daily YouTube Pipeline Summary

| Metric | Value |
| --- | --- |
| Run ID | {metrics["run_id"]} |
| Status | {metrics["status"]} |
| Videos processed | {metrics["videos_processed"]} |
| New videos discovered | {metrics["new_videos_discovered"]} |
| Video errors | {metrics["video_errors"]} |
| Discovery errors | {metrics["discovery_errors"]} |
| Execution time seconds | {metrics["execution_time_seconds"]:.2f} |
| Run date | {metrics["run_date"]} |
| Snapshot date | {metrics["snapshot_date"]} |
| Snapshot time | {metrics["snapshot_time"]} |
| Logical date | {metrics["logical_date"]} |
| Published after | {metrics["published_after"]} |
| Published before | {metrics["published_before"]} |
"""

    with open("pipeline_summary.md", "w", encoding="utf-8") as file:
        file.write(summary)
