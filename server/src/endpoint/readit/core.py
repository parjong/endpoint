from dataclasses import dataclass

from bs4 import BeautifulSoup

import urllib.request
from urllib.parse import ParseResult as URL
from urllib.parse import urlparse
from urllib.parse import urlunparse


@dataclass
class Page:
    url: URL
    title: str

    def url_as_str(self) -> str:
        return urlunparse(self.url)


def page_of_(url: str) -> Page:
    with urllib.request.urlopen(url) as response:
        page_html = response.read()
        soup = BeautifulSoup(page_html, "html.parser")

        page_url = urlparse(response.geturl())
        page_title = soup.title.string

    if page_url.netloc == "www.linkedin.com":
        if page_url.path.startswith("/posts/"):
            page_url = page_url._replace(query="")

    return Page(url=page_url, title=page_title)
