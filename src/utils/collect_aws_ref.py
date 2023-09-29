import os
import requests

from bs4 import BeautifulSoup

AWS_URL_PATH = "./aws_context/urls.txt"
OUTPUT_DIR = "./aws_ref_text"


# bodyを抽出し、"Examples"の項目を削除
def preprocess(soup):
    body = soup.find(attrs={"class": "body"})
    if body.find(id="examples") is not None:
        body.find(id="examples").extract()
    return body


# https://.../<command name>/<subcommand>.htmlの形式となっているため
# commandとsubcommandを切り取り、出力ファイル名に整形
# ただし、例外的にhttps://.../<command name>/<subcommand name>/index.htmlの形式
# のものがある．
def get_output_filepath(url):
    subcommand_name = url.split("/")[-1].replace(".html", "")

    # イレギュラーパターン（../index.html）の処置
    if subcommand_name == "index":
        subcommand_name = url.split("/")[-2]
        command_name = url.split("/")[-3]
    # 正常なパターンの処置
    else:
        command_name = url.split("/")[-2]

    return f"{OUTPUT_DIR}/{command_name}_{subcommand_name}.txt"


def main():
    with open(AWS_URL_PATH, "r") as f:
        urls = f.readlines()

    urls_len = len(set(urls))

    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    for count, url in enumerate(urls):
        url = url.replace("\n", "")

        # 出力ファイルが既存するなら対象URLは処理しない
        output_filepath = get_output_filepath(url)
        if os.path.exists(output_filepath):
            continue

        print(f"{count+1} / {urls_len}")
        print(f"{url}")

        # URLからHTMLを取得し、テキストに変換
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        soup = preprocess(soup)
        ref_text = soup.text

        with open(output_filepath, "w") as f:
            f.write(ref_text)

        print(f"{url} is Done \n")


if __name__ == "__main__":
    main()