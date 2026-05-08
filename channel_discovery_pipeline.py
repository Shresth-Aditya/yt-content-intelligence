from channel_discovery import (
    get_channel_ids_for_niche
)
from logger import setup_logger

logger = setup_logger()

def channel_discovery_run_pipeline():

    niche = "Python"

    channels = get_channel_ids_for_niche(
        niche
    )

    logger.info(
        "Filtered %d channels",
        len(channels)
    )

    for channel in channels:

        logger.info(
            "Channel: %s | Subscribers: %d",
            channel["channel_name"],
            channel["subscribers"]
        )


if __name__ == "__main__":

    channel_discovery_run_pipeline()