import argparse


def get_cl_args_for_dataset_yaml() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--index-id",
        type=str,
        default="user_context_index",
        help="インデックスIDを指定します。",
    )

    parser.add_argument(
        "--context-dir",
        type=str,
        default="./user_context",
        help="コンテキストのファイルが保存されるディレクトリを指定します。",
    )

    return parser.parse_args()
