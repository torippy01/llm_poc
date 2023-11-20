import pytest

from xecretary_core.agents.agent import AgentRunner
from xecretary_core.agents.conf import Config
from xecretary_core.evaluation.evaluation_sentences import EvaluateSentence


@pytest.fixture
def interactive_toml():
    return """
        llm = "gpt-4"
        user_index_dir = "torippy01.llm_poc"
        agent_type = "zero-shot-react-description"
        agent_execution_mode = "interactive"
        eval_sentence = "path/to/input_path"
        md_filepath = "path/to/mdfilepath"
        md_title = "TEST"
        eval_output = "path/to/output_dir"

        [[tools_conf]]
        name = "human"

        [[tools_conf]]
        name = "command_predictor"

        [[tools_conf]]
        name = "parameter_predictor"

        [[tools_conf]]
        name = "shell"

        [[tools_conf]]
        name = "user_context_github_wiki"
        index_dir = "torippy01.llm_poc"
        data_source = "github wiki"
        llm = "gpt-3.5-turbo"
    """


@pytest.fixture
def qa_toml():
    return """
        llm = "gpt-4"
        user_index_dir = "torippy01.llm_poc"
        agent_type = "zero-shot-react-description"
        agent_execution_mode = "qa"
        eval_sentence = "path/to/input_path"
        md_filepath = "path/to/mdfilepath"
        md_title = "TEST"
        eval_output = "path/to/output_dir"

        [[tools_conf]]
        name = "human"

        [[tools_conf]]
        name = "command_predictor"

        [[tools_conf]]
        name = "parameter_predictor"

        [[tools_conf]]
        name = "shell"

        [[tools_conf]]
        name = "user_context_github_wiki"
        index_dir = "torippy01.llm_poc"
        data_source = "github wiki"
        llm = "gpt-3.5-turbo"
    """


@pytest.fixture
def single_toml():
    return """
        llm = "gpt-4"
        user_index_dir = "torippy01.llm_poc"
        agent_type = "zero-shot-react-description"
        agent_execution_mode = "single"
        eval_sentence = "path/to/input_path"
        md_filepath = "path/to/mdfilepath"
        md_title = "TEST"
        eval_output = "path/to/output_dir"

        [[tools_conf]]
        name = "human"

        [[tools_conf]]
        name = "command_predictor"

        [[tools_conf]]
        name = "parameter_predictor"

        [[tools_conf]]
        name = "shell"

        [[tools_conf]]
        name = "user_context_github_wiki"
        index_dir = "torippy01.llm_poc"
        data_source = "github wiki"
        llm = "gpt-3.5-turbo"
    """


def get_conf(tmp_path, toml_str):
    tmp_path.mkdir(parents=True, exist_ok=True)
    toml_path = tmp_path / "test.toml"

    with open(toml_path, "w") as f:
        f.write(toml_str)
    return Config.fetch(toml_path=toml_path)


def test_agent_runner_run(tmp_path, interactive_toml, qa_toml, single_toml, mocker):
    # interactive configuration
    interactive_conf = get_conf(tmp_path / "interactive", interactive_toml)
    agent_runner = AgentRunner(interactive_conf)

    run_agent_with_interactive_mock = mocker.patch.object(
        agent_runner, "run_agent_with_interactive"
    )
    mocker.patch("mdutils.mdutils.MdUtils.create_md_file")
    mocker.patch(
        (
            "xecretary_core.evaluation.evaluation_sentences.EvaluateSentence."
            "from_list_to_yaml"
        ),
        return_value=None,
    )
    agent_runner.run()
    run_agent_with_interactive_mock.assert_called_once()

    # qa configuration
    qa_conf = get_conf(tmp_path, qa_toml)
    agent_runner = AgentRunner(qa_conf)
    run_agent_with_Q_and_A_mock = mocker.patch.object(
        agent_runner, "run_agent_with_Q_and_A"
    )
    agent_runner.run()
    run_agent_with_Q_and_A_mock.assert_called_once()

    # single configuration
    single_conf = get_conf(tmp_path, single_toml)
    agent_runner = AgentRunner(single_conf)
    run_agent_with_single_action_mock = mocker.patch.object(
        agent_runner, "run_agent_with_single_action"
    )
    agent_runner.run()
    run_agent_with_single_action_mock.assert_called_once()


def test_run_agent_with_interactive(tmp_path, interactive_toml, mocker):
    conf = get_conf(tmp_path, interactive_toml)
    agent_runner = AgentRunner(conf)

    agent_executor_mock = mocker.patch.object(agent_runner, "agent_executor")
    mock_inputs = iter(["こんにちは", "exit"])
    mocker.patch("builtins.input", side_effect=mock_inputs)
    agent_runner.run_agent_with_interactive()
    agent_executor_mock.assert_called_once()


def test_run_agent_with_Q_and_A(tmp_path, qa_toml, mocker):
    conf = get_conf(tmp_path, qa_toml)
    agent_runner = AgentRunner(conf)
    agent_executor_mock = mocker.patch.object(agent_runner, "agent_executor")
    mocker.patch(
        "xecretary_core.evaluation.evaluation_sentences.EvaluateSentence.from_yaml_to_list",
        return_value=[
            EvaluateSentence(
                input="input text",
                output="output text",
                human_answer=None,
                evaluation=None,
            )
        ],
    )
    agent_runner.run_agent_with_Q_and_A()
    agent_executor_mock.assert_called_once()


def test_run_agent_with_single_action(tmp_path, single_toml, mocker):
    conf = get_conf(tmp_path, single_toml)
    agent_runner = AgentRunner(conf)

    # use user_massage case
    input_text = "Hello"
    output_text = "Hello, how are you?"
    agent_executor_mock = mocker.patch.object(
        agent_runner,
        "agent_executor",
    )
    agent_runner.run_agent_with_single_action(user_message=input_text)
    agent_executor_mock.assert_called_once()

    # does not use user_massage and appropriate case
    mocker.patch.object(agent_runner, "agent_executor")
    mocker.patch(
        "xecretary_core.evaluation.evaluation_sentences.EvaluateSentence.from_yaml_to_list",
        return_value=[
            EvaluateSentence(
                input=input_text, output=output_text, human_answer=None, evaluation=None
            )
        ],
    )
    agent_runner.run_agent_with_single_action()
    agent_executor_mock.assert_called_once()
