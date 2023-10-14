"""
AWSのサブコマンドのリファレンスURLを全件取得するコードです。
実行時間は1時間30分 ～ 2時間程度です。
"""

import time

import requests
from bs4 import BeautifulSoup

ROOT_URL = (
    "https://awscli.amazonaws.com/v2/documentation/api/latest/reference/index.html"
)


def get_html(url):
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    return response.text


def get_blob(url):
    return url[: url.rfind("/") + 1]


def get_urls(ref_url):
    html = get_html(ref_url)
    blob = get_blob(ref_url)

    lis = BeautifulSoup(html, "html.parser").select("li.toctree-l1")
    urls = list()
    for li in lis:
        a = li.find("a")
        url = f'{blob}{a.get("href")}'
        if url is not None:
            urls.append(url)
    return urls


def main():
    print("AWS CLIのコマンドのURLを取得しています。")
    command_urls = get_urls(ROOT_URL)
    print("取得完了")

    urls = list()

    for i, command_url in enumerate(command_urls):
        time.sleep(15)
        print(f"{command_url} 中のサブコマンドのURLを取得しています。")
        print(f"{i + 1} / {len(command_urls)}")
        subcommand_urls = get_urls(command_url)
        urls.extend(subcommand_urls)
        print("取得完了")

    write_text = "\n".join(urls)
    with open("urls.txt", "w") as f:
        f.write(write_text)


if __name__ == "__main__":
    main()
