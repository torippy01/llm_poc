import pytest

from xecretary_core.tools.conf import ToolConfig
from xecretary_core.tools.tool_aws import CommandPredictorTool, ParameterPredictorTool
from xecretary_core.tools.tool_shell import ShellAndSummarizeTool


@pytest.fixture
def command_predictor_conf():
    return {"name": "command_predictor"}


@pytest.fixture
def parameter_predictor_conf():
    return {"name": "parameter_predictor"}


@pytest.fixture
def shell_conf():
    return {"name": "shell"}


@pytest.fixture
def human_conf():
    return {"name": "human"}


@pytest.fixture
def user_context_predictor_conf():
    return {
        "name": "context_predictor",
        "index_dir": "tmp/index/",
        "data_source": "document",
        "llm": "gpt4",
    }


def test_get_tool(
    mocker,
    command_predictor_conf,
    parameter_predictor_conf,
    shell_conf,
    human_conf,
    user_context_predictor_conf,
):
    # command predictor configuration case
    tool_config = ToolConfig(command_predictor_conf)
    assert tool_config.get_tool() == CommandPredictorTool()

    # parameter predictor cofiguration case
    tool_config = ToolConfig(parameter_predictor_conf)
    assert tool_config.get_tool() == ParameterPredictorTool()

    # shell tool configuration case
    tool_config = ToolConfig(shell_conf)
    assert isinstance(tool_config.get_tool(), ShellAndSummarizeTool)

    # human tool configuration case
    create_HumanTool_mock = mocker.patch("xecretary_core.tools.conf.create_HumanTool")
    tool_config = ToolConfig(human_conf).get_tool()
    create_HumanTool_mock.assert_called_once()

    # user context predictor case
    create_user_context_predictor_tool_mock = mocker.patch(
        "xecretary_core.tools.conf.create_user_context_predictor_tool"
    )
    ToolConfig(user_context_predictor_conf).get_tool()
    create_user_context_predictor_tool_mock.assert_called_once()


def test_fetch(
    command_predictor_conf,
    parameter_predictor_conf,
    shell_conf,
    human_conf,
    user_context_predictor_conf,
):
    tool_conf_list = [
        command_predictor_conf,
        parameter_predictor_conf,
        shell_conf,
        human_conf,
        user_context_predictor_conf,
    ]
    expect = ToolConfig.fetch(tool_conf_list)

    for e, answer in zip(expect, tool_conf_list):
        assert e.name == answer["name"]
        assert e.index_dir == answer.get("index_dir")
        assert e.data_source == answer.get("data_source")
        assert e.llm_name == answer.get("llm")
