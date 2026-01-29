from dataclasses import dataclass

from bs4 import BeautifulSoup
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from pydantic import Field
import requests
from urllib.parse import ParseResult as URL
from urllib.parse import urlparse
from urllib.parse import urlunparse


class Summary(BaseModel):
    title: str = Field(
        description="The title of concise main title of the article or page"
    )
    date: str = Field(
        description="The issue or publication date as YYYY/MM/DD format (????/??/?? if unknown)"
    )


@dataclass
class Page:
    url: URL
    body: str

    def url_as_str(self) -> str:
        return urlunparse(self.url)


def page_of_(url: str) -> Page:
    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124"
        },
    )
    response.raise_for_status()

    page_url = urlparse(response.url)
    soup = BeautifulSoup(response.text, "html.parser")

    if page_url.netloc == "www.linkedin.com":
        if page_url.path.startswith("/posts/"):
            page_url = page_url._replace(query="")

    return Page(url=page_url, body=soup.body)


def summary_of_(page: Page) -> Summary:
    prompt = ChatPromptTemplate.from_template("""
    Analyze the following content from a webpage and extract two pieces of information:
    1. The concise main title of the article or page.
    2. The issue or publication date as YYYY/MM/DD format (if available).
       - If not available, state "????/??/??".

    Format your answer as a JSON object with keys "date" and "title".

    Content: {content}
    """)
    structured_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash"
    ).with_structured_output(Summary)

    chain = prompt | structured_llm

    return chain.invoke({"content": page.body})
