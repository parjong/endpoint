import click


from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport as HTTPTransport

import logging
import logging.config
import os
from pprint import pformat
import tomllib

config = {
    "version": 1,
    "disable_existing_loggers": False,  # allows other loggers (e.g. library loggers) to work
    "formatters": {
        "standard": {
            "format": "[%(levelname)s] %(name)s %(filename)s:%(lineno)d %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "loggers": {
        "entrypoint": {
            "handlers": ["console"],
            "level": os.environ.get("ENDPOINT_LOG_LEVEL", "INFO").upper(),
            "propagate": False,
        },
        "": {
            "handlers": ["console"],
            "level": "WARNING",
        },
    },
}
logging.config.dictConfig(config)

logger = logging.getLogger("entrypoint")
logger.setLevel(os.environ.get("ENTRYPOINT_LOG_LEVEL", "INFO").upper())


@click.group
@click.option("--use-config-at", "config_toml_path", default="endpoint.config.toml")
@click.pass_context
def main(ctx, config_toml_path) -> None:
    ctx.ensure_object(dict)

    with open(config_toml_path, "rb") as f:
        ctx.obj = tomllib.load(f)

    logger.debug("config loaded")
    logger.debug(pformat(ctx.obj))

    pass


@main.group()
@click.pass_context
def readit(ctx) -> None:
    """readit! service entrypoint"""
    pass


addDraftIssue = gql("""
  mutation enqueue($targetProjectId: ID!, $url: String!) {
    addProjectV2DraftIssue(input: {
      projectId: $targetProjectId,
      title: $url,
      body: \"\",
    }) { projectItem { id } }
  }
""")


@readit.command()
@click.argument("article_url")
@click.pass_context
def enqueue(ctx, article_url: str) -> None:
    """Add URL to processing queue"""

    api_url = os.environ["GITHUB_GRAPHQL_URL"]
    token = os.environ["OWNER_TOKEN"]

    transport = HTTPTransport(url=api_url, headers={"Authorization": f"Bearer {token}"})
    client = Client(transport=transport, fetch_schema_from_transport=True)

    for queue in ctx.obj["readit"]["queue"]:
        logger.debug(queue)
        queue_type: str = queue["type"]

        if queue_type == "GITHUB_PROJECT_V2":
            result = client.execute(
                addDraftIssue,
                variable_values={
                    "targetProjectId": queue["id"],
                    "url": article_url,
                },
            )
            logger.debug(result)
        else:
            raise Exception(f"Unsupported queue type: {queue_type}")

    pass
