import asyncio
import pytest

from xecretary_core.tools.tool_aws import (
    CommandPredictorTool,
    ParameterPredictorTool,
    get_aws_cli_version,
)


@pytest.fixture
def encoded_aws_cli_version():
    return (
        b"aws-cli/2.13.18 Python/3.11.5 Linux/5.15.133.1-microsoft-"
        b"standard-WSL2 exe/x86_64.ubuntu.22 prompt/off\n"
    )


@pytest.fixture
def get_aws_cli_version_mock(mocker, encoded_aws_cli_version):
    return mocker.patch(
        "xecretary_core.tools.tool_aws.subprocess.check_output",
        return_value=encoded_aws_cli_version,
    )


@pytest.fixture
def get_gpt_response_mock(mocker):
    return mocker.patch("xecretary_core.tools.tool_aws.get_gpt_response")


@pytest.fixture
def get_event_loop_mock(mocker):
    run_in_executor_mock = mocker.patch.object(
        asyncio.get_event_loop(), "run_in_executor", return_value=asyncio.Future()
    )
    # to ensure that the Future completes immediately.
    run_in_executor_mock.return_value.set_result("test response")
    return run_in_executor_mock


def test_get_aws_cli_version(get_aws_cli_version_mock):
    get_aws_cli_version()
    get_aws_cli_version_mock.assert_called_once()


def test_command_predictor_tool_run(get_gpt_response_mock):
    tool = CommandPredictorTool()
    tool._run("Hello")
    get_gpt_response_mock.assert_called_once()


@pytest.mark.asyncio
async def test_command_predictor_tool_arun(get_event_loop_mock):
    tool = CommandPredictorTool()
    await tool._arun("Hello")
    get_event_loop_mock.assert_called_once()


def test_parameter_predictor_tool_run(get_gpt_response_mock):
    tool = ParameterPredictorTool()
    tool._run("Hello")
    get_gpt_response_mock.assert_called_once()


@pytest.mark.asyncio
async def test_parameter_predictor_tool_arun(get_event_loop_mock):
    tool = ParameterPredictorTool()
    await tool._arun("Hello")
    get_event_loop_mock.assert_called_once()
