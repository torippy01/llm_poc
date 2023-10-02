import argparse
import yaml
import openai
import os

from dotenv import load_dotenv


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset-path",
        type=str,
        default="./repo/ai_answer/evaluation.yaml",
        help="推論用LLM名を指定します。"
    )
    return parser.parse_args()

def set_config():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")


def load_dataset(dataset_path):
    with open(dataset_path) as f:
        datasets = yaml.safe_load(f)
    return datasets


def evaluate(sentence1, sentence2):
    content = f"""
        次の文章１と文章２の文章はAWS CLIの実行結果、またはプロジェクトについて述べているものです。
        この２つの文章の意味がどの程度似ているかを、<評価値>/5の形式5段階評価してください。
        また、なぜそのような評価をしたのかを説明してください。
        評価は、以下のルールを設けます。

        - 評価:5
            * 文章が完全に同一
        - 評価:4
            * 文章の一部が異なるが、文意は同一
            * AWS CLIのパラメータとなるような値が完全一致
        - 評価:3
            * 評価元の文の意味に過不足がある
            * AWS CLIのパラメータとなるような値が複数ある場合は、半分以上一致
            * AWS CLIのパラメータとなるような値が単一の場合は値が完全一致
        - 評価:2
            * 評価元の文に同一の話題が述べられているが、意味が不一致
            * AWS CLIのパラメータとなるような値が1～4割一致
            * AWS CLIのパラメータとなるような値が単一の場合は値が不一致
        - 評価:1
            * 文意が全く異なる

        文章１： {sentence1}
        文章２： {sentence2}
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": content}
        ]
    )
    return response.choices[0]["message"]["content"].strip()


def main():
    set_config()
    args = get_args()
    datasets = load_dataset(args.dataset_path)

    evaluations = list()
    for dataset in datasets:
        print(dataset["answer"])
        print(dataset["final_answer"])
        evaluation_value = evaluate(
            sentence1=dataset["answer"],
            sentence2=dataset["final_answer"]
        )
        print(evaluation_value)
        evaluations.append(evaluation_value)

    with open("./res.txt", "w") as f:
        f.writelines(evaluations)

if __name__ == "__main__":
    main()