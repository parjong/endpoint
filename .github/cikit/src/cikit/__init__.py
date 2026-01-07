import click
from github import Github
import requests


import os


@click.group
def main() -> None:
    pass


@main.command
@click.option("-o", "local_path")
@click.argument("remote_path")
def download_gist(local_path: str, remote_path: str):
    token = os.environ["GIST_DOWNLOAD_TOKEN"]

    g = Github(token)

    # remote path example: https://gist.github.com/parjong/378e7f8c01b32f424459543ab310261e/sample.html
    remote_path_entries = remote_path.rstrip().split("/")

    gist_id = remote_path_entries[-2]
    gist_filename = remote_path_entries[-1]

    gist = g.get_gist(gist_id)

    gist_url = gist.files[gist_filename].raw_url

    gist_content = requests.get(gist_url).text

    with open(local_path, "w") as f:
        print(gist_content, file=f)

    pass
