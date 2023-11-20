import pytest

from mdutils.mdutils import MdUtils
from time import time
from uuid import uuid4
from langchain.schema.agent import AgentAction

from xecretary_core.callback.callback import CustomCallbackHandler


@pytest.fixture
def serialized():
    return {
        "lc": 1,
        "type": "constructor",
        "id": ["langchain", "chains", "llm", "LLMChain"],
        "kwargs": {
            "llm": {
                "lc": 1,
                "type": "constructor",
                "id": ["langchain", "chat_models", "openai", "ChatOpenAI"],
                "kwargs": {
                    "temperature": 0.0,
                    "model_name": "gpt-4",
                    "openai_api_key": {
                        "lc": 1,
                        "type": "secret",
                        "id": ["OPENAI_API_KEY"],
                    },
                },
            },
            "prompt": {
                "lc": 1,
                "type": "constructor",
                "id": ["langchain", "prompts", "prompt", "PromptTemplate"],
                "kwargs": {
                    "template": (
                        "Answer the following questions as best you can."
                        " You have access to the following tools:\n\n"
                        "command_predictor: \n        バージョンaws-cli/2.13.18 "
                        "Python/3.11.5 Linux/5.15.133.1-microsoft-standard-WSL2 "
                        "exe/x86_64.ubuntu.22 prompt/offのAWS CLIコマンドを取得する"
                        "ツール\n    \nparameter_predictor: \n        バージョン"
                        "aws-cli/2.13.18 Python/3.11.5 Linux/5.15.133.1-microsoft-"
                        "standard-WSL2 exe/x86_64.ubuntu.22 prompt/offのAWS CLI"
                        "コマンドの引数を取得するツール\n        またこのツールは、"
                        "出力結果の文字数が膨大であることが予測されるならば、\n        "
                        "フィルタまたは`jq`コマンド、`grep`コマンドを積極的に用いて、"
                        "\n        必要な情報のみ抽出するコマンドに整形する。\n    \n"
                        "terminal: Run shell commands on this Linux machine."
                        "\nuser_context_from_github wiki: \n        ユーザーしか"
                        "知らない知識をgithub wikiから取得するツール\n        "
                        "\n\nUse the following format:\n\nQuestion: the input "
                        "question you must answer\nThought: you should always "
                        "think about what to do\nAction: the action to take, "
                        "should be one of [command_predictor, parameter_predictor, "
                        "terminal, user_context_from_github wiki]\nAction Input: "
                        "the input to the action\nObservation: the result of the "
                        "action\n... (this Thought/Action/Action Input/Observation "
                        "can repeat N times)\nThought: I now know the final "
                        "answer\nFinal Answer: the final answer to the original "
                        "input question\n\nBegin!\n\nQuestion: {input}\nThought:"
                        "{agent_scratchpad}"
                    ),
                    "input_variables": ["input", "agent_scratchpad"],
                    "template_format": "f-string",
                },
            },
        },
    }


@pytest.fixture
def inputs():
    return {
        "input": "このプロジェクトのエンジニアは誰ですか？",
        "chat_history": [],
        "agent_scratchpad": "",
        "stop": ["\nObservation:", "\n\tObservation:"],
    }


@pytest.fixture
def outputs():
    return {
        "output": (
            "このプロジェクトのエンジニアは金田\u3000正太郎さん, "
            "島\u3000鉄雄さん, 山形さん, 甲斐さん, ケイさん, "
            "ミヤコさんです。"
        ),
        "intermediate_steps": [
            (
                AgentAction(
                    tool="user_context_from_github wiki",
                    tool_input="プロジェクトのエンジニア",
                    log=(
                        "この情報はGitHubのwikiに記載されている可能性がある。"
                        "\nAction: user_context_from_github wiki\n"
                        "Action Input: プロジェクトのエンジニア"
                    ),
                ),
                (
                    "金田\u3000正太郎さん, 島\u3000鉄雄さん, 山形さん,"
                    "甲斐さん, ケイさん, ミヤコさん"
                ),
            )
        ],
    }


@pytest.fixture
def handler():
    md_file = MdUtils(file_name="test.md")
    return CustomCallbackHandler(md_file=md_file)


@pytest.fixture
def run_id():
    return uuid4()


@pytest.mark.freeze_time("2023-12-31")
def test_on_chain_start(serialized, handler, run_id, inputs):
    handler.on_chain_start(inputs=inputs, run_id=run_id, serialized=serialized)

    assert handler.user_input == inputs["input"]
    assert handler.chain_start_time == time()


def test_on_text(capsys, handler):
    # small text case
    small_text = "Hello World"
    on_text_result = handler.on_text(text=small_text)
    captured = capsys.readouterr()
    assert captured.out is ""
    assert on_text_result is None

    # large text case
    with open("src/tests/callback/large_text.txt", "r") as f:
        large_text = f.read()

    handler.on_text(text=large_text)
    captured = capsys.readouterr()
    assert captured.out == "token count is 5056\n"


def test_on_chain_end(handler, run_id, inputs, outputs):
    handler.user_input = inputs["input"]

    # in case: appropriate `outputs`
    assert (
        handler.on_chain_end(
            outputs=outputs,
            run_id=run_id,
            parent_run_id=uuid4(),
        )
        is None
    )

    # in case: `outputs` is None object
    assert (
        handler.on_chain_end(
            outputs=dict(),
            run_id=run_id,
            parent_run_id=uuid4(),
        )
        is None
    )
