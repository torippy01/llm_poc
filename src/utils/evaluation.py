import argparse
import openai
import os

from dotenv import load_dotenv
from schema import EvaluateSentences, EvaluateSentence


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset-path",
        type=str,
        default="./eval_sentence/evaluation_human_eval.yaml",
        help="推論用LLM名を指定します。"
    )
    return parser.parse_args()

def set_config():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")


def evaluate(sentences: EvaluateSentence) -> EvaluateSentence:
    content = f"""
        回答文は、質問文に対する回答が書かれています。
        評価文に基づいて、回答文の評価を行いなさい．
        評価は、１から３の３段階評価とします。
        評価のフォーマットは、`評価：評価数`とします。
        また、なぜその評価を行ったかを説明しなさい。

        質問文： {sentences.input}
        回答文： {sentences.output}
        評価文： {sentences.human_answer}
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": content}
        ]
    ).choices[0]["message"]["content"].strip()
    sentences.evaluation = response
    return sentences


def main():
    set_config()
    args = get_args()
    dataset = EvaluateSentences()
    dataset.from_yaml(args.dataset_path)
    results = EvaluateSentences()

    for sentences in dataset:
        result: EvaluateSentence = evaluate(sentences)
        results.append(result)

    results.to_yaml("repo.yaml")


if __name__ == "__main__":
    main()