import click

from logging import getLogger
import os

from endpoint.readit.core import page_of_
from endpoint.readit.core import summary_of_
from endpoint.readit.sink.personal import Sink as PersonalSink
from endpoint.readit.sink.queue_v2 import Sink as V2QueueSink


logger = getLogger(__name__)
logger.setLevel(os.environ.get("ENTRYPOINT_LOG_LEVEL", "INFO").upper())


@click.command()
@click.option("--url", required=True)
@click.option("--to", "names", multiple=True)
def main(url: str, names) -> None:
    owner_token = os.environ["OWNER_TOKEN"]

    logger.info("Send '%s' to '%s'", url, names)

    registry = {
        "personal": PersonalSink(token=owner_token),
        "queue_v2": V2QueueSink(token=owner_token),
    }
    sinks = [registry[name] for name in names]

    page = page_of_(url)
    logger.info(page)

    summary = summary_of_(page)

    for sink in sinks:
        sink.add(page, summary)

    logger.info("Done")
