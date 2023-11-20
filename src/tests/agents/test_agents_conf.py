import os
import pytest

from langchain.tools.human import HumanInputRun
from langchain.agents import AgentType
from xecretary_core.agents.conf import Config
from xecretary_core.tools.conf import ToolConfig
from xecretary_core.tools.tool_aws import CommandPredictorTool, ParameterPredictorTool
from xecretary_core.tools.tool_shell import ShellAndSummarizeTool
from xecretary_core.tools.tool_uc_predictor import create_user_context_predictor_tool


@pytest.fixture
def appropriate_config():
    # 適正なConfオブジェクトを提供するfixture
    tool_confs = [
        ToolConfig({"name": "shell"}),
        ToolConfig({"name": "command_predictor"}),
        ToolConfig({"name": "parameter_predictor"}),
        ToolConfig({"name": "human"}),
        ToolConfig(
            {
                "name": "user_context_github_wiki",
                "index_dir": "torippy01.llm_poc",
                "data_source": "github_wiki",
                "llm": "gpt-3.5-turbo",
            }
        ),
    ]

    conf = Config(
        agent_execution_mode="SINGLE",
        agent_type="zero-shot-react-description",
        llm_name="gpt-4",
        user_index_dir="torippy01.llm_poc",
        pull="",
        tool_confs=tool_confs,
        eval_sentences_input_path="path/to/input_path",
        eval_output_dir="path/to/output_dir",
        md_filepath="path/to/mdfilepath",
        md_title="TEST",
    )

    return conf, tool_confs


@pytest.fixture
def non_tool_confs_config():
    # tool_confsの要素がないケース．例外発出を想定
    return Config(
        agent_execution_mode="single",
        agent_type="zero-shot-react-description",
        llm_name="gpt-4",
        user_index_dir="torippy01.llm_poc",
        pull=None,
        tool_confs=[],
        eval_sentences_input_path="path/to/input_path",
        eval_output_dir="path/to/output_dir",
        md_filepath="path/to/mdfilepath",
        md_title="TEST",
    )


@pytest.fixture
def non_execution_mode_toml():
    return """
        llm = "gpt-4"
        user_index_dir = "torippy01.llm_poc"
        agent_type = "zero-shot-react-description"
        eval_sentence = "path/to/input_path"
        md_filepath = "./repo/results/test.md"
        md_title = "TEST"
        eval_output = "path/to/output_dir"

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
def non_eval_sentence_toml():
    return """
        llm = "gpt-4"
        user_index_dir = "torippy01.llm_poc"
        agent_type = "zero-shot-react-description"
        agent_execution_mode = "single"
        md_filepath = "path/to/mdfilepath"
        md_title = "test"
        eval_output = "path/to/output_dir"

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
def appropriate_toml():
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


def test_get_tools_pass(appropriate_config):
    conf, tool_confs = appropriate_config
    expect = conf.get_tools()

    uc_predictor_tool = create_user_context_predictor_tool(
        tool_confs[4].name,
        tool_confs[4].index_dir,
        tool_confs[4].data_source,
        tool_confs[4].llm_name,
    )

    assert len(expect) == 5
    assert isinstance(expect[0], ShellAndSummarizeTool)
    assert isinstance(expect[1], CommandPredictorTool)
    assert isinstance(expect[2], ParameterPredictorTool)
    assert isinstance(expect[3], HumanInputRun)
    assert str(expect[4].__class__) == str(uc_predictor_tool.__class__)


def test_get_tools_runtime_error(non_tool_confs_config):
    with pytest.raises(RuntimeError) as e:
        non_tool_confs_config.get_tools()

    assert str(e.value) == "Config error : set 'tool_confs'"


def test_get_name_of_tools(appropriate_config):
    conf, _ = appropriate_config
    assert conf.get_name_of_tools() == (
        "shell, command_predictor, parameter_predictor, human, "
        "user_context_github_wiki"
    )


def test_generate_md_file(appropriate_config):
    conf, _ = appropriate_config
    expect = conf.generate_md_file().get_md_text()
    with open("./src/tests/agents/md_content.md", "r") as f:
        answer = f.read()

    assert expect == answer


def test_fetch_non_toml():
    with pytest.raises(ValueError) as e:
        Config.fetch(toml_path=None)
    assert str(e.value) == "Invalid value : 'toml_path'"


def test_fetch_non_agent_execution_mode(tmp_path, non_execution_mode_toml):
    toml_path = tmp_path / "test.toml"

    with open(toml_path, "w") as f:
        f.write(non_execution_mode_toml)

    with pytest.raises(ValueError) as e:
        Config.fetch(toml_path=toml_path)

    assert str(e.value) == "Config error : set 'agent_execution_mode'"


def test_fetch_non_eval_sentence(tmp_path, non_eval_sentence_toml):
    toml_path = tmp_path / "test.toml"

    with open(toml_path, "w") as f:
        f.write(non_eval_sentence_toml)

    with pytest.raises(ValueError) as e:
        Config.fetch(toml_path=toml_path)

    assert str(e.value) == "Config error : set 'eval_sentence'"


def test_fetch_approval(tmp_path, appropriate_toml, appropriate_config):
    toml_path = tmp_path / "test.toml"

    with open(toml_path, "w") as f:
        f.write(appropriate_toml)

    expect = Config.fetch(toml_path=toml_path)
    answer, _ = appropriate_config

    assert expect.agent_execution_mode == "SINGLE"
    assert expect.agent_type == AgentType.ZERO_SHOT_REACT_DESCRIPTION
    assert expect.llm_name == answer.llm_name
    assert expect.user_index_dir == answer.user_index_dir
    assert expect.pull is None
    assert expect.tool_confs[0].name == "human"
    assert expect.tool_confs[1].name == "command_predictor"
    assert expect.tool_confs[2].name == "parameter_predictor"
    assert expect.tool_confs[3].name == "shell"
    assert expect.tool_confs[4].name == "user_context_github_wiki"
    assert expect.tool_confs[4].index_dir == "torippy01.llm_poc"
    assert expect.tool_confs[4].data_source == "github wiki"
    assert expect.tool_confs[4].llm_name == "gpt-3.5-turbo"
    assert expect.eval_sentences_input_path == answer.eval_sentences_input_path
    assert expect.eval_output_dir == answer.eval_output_dir
    assert expect.md_filepath == answer.md_filepath
    assert expect.md_title == answer.md_title
