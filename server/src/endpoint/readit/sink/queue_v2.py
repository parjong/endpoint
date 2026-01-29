from gql import Client
from gql import gql
from gql.transport.requests import RequestsHTTPTransport as HTTPTransport

from logging import getLogger

from endpoint.readit.core import Page


logger = getLogger(__name__)


class AddProjectV2DraftIssue:
    QUERY = gql("""
    mutation ($projectId: ID!, $title: String!, $body: String!) {
      addProjectV2DraftIssue(input: {
        projectId: $projectId,
        title: $title,
        body: $body,
      }) { projectItem { id } }
    }
    """)

    def __init__(self, *, projectId: str, title: str, body: str):
        self._values = {
            "projectId": projectId,
            "title": title,
            "body": body,
        }

    def execute(self, client):
        result = client.execute(self.QUERY, variable_values=self._values)
        logger.debug(result)
        pass


class Sink:
    PROJECT_ID = "PVT_kwHOAOPA3c4BNgtr"

    def __init__(self, *, token: str):
        github_graphql_url = "https://api.github.com/graphql"

        self._client = Client(
            transport=HTTPTransport(
                url=github_graphql_url,
                headers={"Authorization": f"Bearer {token}"},
            )
        )

    def add(self, page: Page):
        AddProjectV2DraftIssue(
            projectId=self.PROJECT_ID, title=page.title, body=page.url_as_str()
        ).execute(self._client)
