import arxiv

from gql import Client
from gql import gql
from gql.transport.requests import RequestsHTTPTransport as HTTPTransport

from logging import getLogger

from endpoint.readit.core import Page


logger = getLogger(__name__)


class CreateDiscussion:
    QUERY = gql("""
    mutation ($repositoryId: ID!, $categoryId: ID!, $title: String!, $body: String!) {
      createDiscussion(input: {
          repositoryId: $repositoryId,
          categoryId: $categoryId,
title: $title,
          body: $body
      }) { discussion { id } }
    }
    """)

    def __init__(self, *, repositoryId: str, categoryId: str, title: str, body: str):
        self._values = {
            "repositoryId": repositoryId,
            "categoryId": categoryId,
            "title": title,
            "body": body,
        }

    def execute(self, client):
        result = client.execute(self.QUERY, variable_values=self._values)
        logger.debug(result)
        pass


class PersonalStorage:
    REPOSITORY_ID = "MDEwOlJlcG9zaXRvcnk4NTc2NDg5Mw=="

    def __init__(self, *, token: str):
        github_graphql_url = "https://api.github.com/graphql"

        self._client = Client(
            transport=HTTPTransport(
                url=github_graphql_url,
                headers={"Authorization": f"Bearer {token}"},
            )
        )

    def add_arXiv_article(self, arxiv_id: str):
        search = arxiv.Search(id_list=[arxiv_id])
        results = list(search.results())
        paper = results[0]

        lines = [f"https://arxiv.org/abs/{arxiv_id}", "", f"> {paper.summary}"]

        CreateDiscussion(
            repositoryId=self.REPOSITORY_ID,
            categoryId="DIC_kwDOBRyrHc4Cz64i",
            title=f"[{paper.published.year}] {paper.title}",
            body="\n".join(lines),
        ).execute(self._client)

    def add_other_article(self, page: Page):
        CreateDiscussion(
            repositoryId=self.REPOSITORY_ID,
            categoryId="DIC_kwDOBRyrHc4Cz61s",
            title=f"[{page.date}] {page.title}",
            body=f"{page.url_as_str()}",
        ).execute(self._client)


class Sink:
    def __init__(self, *, token: str):
        self._storage = PersonalStorage(token=token)

    def add(self, page: Page):
        if page.url.netloc == "arxiv.org":
            arxiv_id = page.url.path.split("/")[-1]
            self._storage.add_arXiv_article(arxiv_id)
            # TODO Implement fallback to "other" feature
        else:
            self._storage.add_other_article(page)

        logger.info("Done")
