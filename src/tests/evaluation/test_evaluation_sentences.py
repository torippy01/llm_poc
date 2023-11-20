import pytest
from xecretary_core.utils.utility import get_gpt_response

from xecretary_core.evaluation.evaluation_sentences import EvaluateSentence


@pytest.fixture
def prop():
    return {
        "input": "Hello",
        "output": "Hello how are you",
        "human_answer": "Appropriately responding to greetings.",
        "evaluation": "3",
    }


@pytest.fixture
def yaml_contents():
    return """
- evaluation: "3"
  human_answer: "Appropriately responding to greetings."
  input: "Hello"
  output: "Hello how are you"

    """


def test_evaluation(mocker, prop):
    get_gpt_response_magic_mock = mocker.patch(
        "xecretary_core.evaluation.evaluation_sentences.get_gpt_response",
    )

    eval_sentence = EvaluateSentence(**prop)
    eval_sentence.evaluate()
    get_gpt_response_magic_mock.assert_called_once()


def test_to_dict(prop):
    eval_sentence = EvaluateSentence(**prop)
    assert eval_sentence.to_dict() == prop


def test_from_dict(prop):
    eval_sentence = EvaluateSentence.from_dict(prop)
    assert eval_sentence.input == prop["input"]
    assert eval_sentence.output == prop["output"]
    assert eval_sentence.human_answer == prop["human_answer"]
    assert eval_sentence.evaluation == prop["evaluation"]


def test_from_yaml_to_list(tmp_path, yaml_contents, prop):
    # not set yaml_filepath case
    with pytest.raises(ValueError) as e:
        eval_sentence = EvaluateSentence.from_yaml_to_list(yaml_filepath=None)
    assert str(e.value) == "Invalid value : yaml_filepath"

    # set yaml_filepath and do not exist contents case
    yaml_filepath = tmp_path / "test.yaml"
    with open(yaml_filepath, "w") as f:
        f.write("")

    with pytest.raises(RuntimeError) as e:
        eval_sentence = EvaluateSentence.from_yaml_to_list(yaml_filepath=yaml_filepath)
    assert str(e.value) == "No sentences to evaluate in yaml file."

    # set appropriate yaml_filepath
    yaml_filepath = tmp_path / "test.yaml"
    with open(yaml_filepath, "w") as f:
        f.write(yaml_contents)

    expect = EvaluateSentence.from_yaml_to_list(yaml_filepath)
    answer = [EvaluateSentence(**prop)]
    assert expect == answer


def test_from_list_to_yaml(tmp_path, prop, yaml_contents):
    # appropriate case
    list_eval_sentence = [EvaluateSentence(**prop)]
    yaml_filepath = tmp_path / "test.yaml"
    EvaluateSentence.from_list_to_yaml(list_eval_sentence, yaml_filepath)
    with open(yaml_filepath, "r") as f:
        expect = f.read()
    with open("src/tests/evaluation/eval_sentence.txt", "r") as f:
        answer = f.read()
    assert expect == answer

    # not exist list contents case
    with pytest.raises(RuntimeError) as e:
        EvaluateSentence.from_list_to_yaml([], yaml_filepath)
    assert str(e.value) == "No sentences to evaluate in list."
