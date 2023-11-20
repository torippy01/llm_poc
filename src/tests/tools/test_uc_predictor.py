import asyncio
import pytest

from llama_index import (
    StorageContext,
    ServiceContext,
)

from xecretary_core.tools.tool_uc_predictor import (
    get_query_engine,
    create_user_context_predictor_tool,
)
from xecretary_core.utils.utility import create_llm


@pytest.fixture
def from_defaults_mock(mocker):
    return mocker.patch.object(StorageContext, "from_defaults")


@pytest.fixture
def load_index_from_storage_mock(mocker):
    return mocker.patch(
        "xecretary_core.tools.tool_uc_predictor.load_index_from_storage"
    )


@pytest.fixture
def from_defaults_context_mock(mocker):
    return mocker.patch.object(ServiceContext, "from_defaults")


@pytest.fixture
def prop():
    return {
        "name": "user_context_tool",
        "index_dir": "user_context",
        "data_source": "document",
        "llm_name": "gpt-4",
    }


@pytest.fixture
def get_query_engine_mock(mocker):
    return mocker.patch("xecretary_core.tools.tool_uc_predictor.get_query_engine")


@pytest.fixture
def get_event_loop_mock(mocker):
    run_in_executor_mock = mocker.patch.object(
        asyncio.get_event_loop(), "run_in_executor", return_value=asyncio.Future()
    )
    # to ensure that the Future completes immediately.
    run_in_executor_mock.return_value.set_result("test response")
    return run_in_executor_mock


def test_get_query_engine(
    from_defaults_mock,
    load_index_from_storage_mock,
    from_defaults_context_mock,
):
    llm = create_llm("gpt-4")
    _ = get_query_engine("user_context_index", llm)

    from_defaults_mock.assert_called_once()
    load_index_from_storage_mock.assert_called_once()
    from_defaults_context_mock.assert_called_once()
    load_index_from_storage_mock.return_value.as_query_engine.assert_called_once()


def test_create_user_context_predictor_tool_run(prop, get_query_engine_mock):
    tool = create_user_context_predictor_tool(**prop)
    tool._run("Hello")
    get_query_engine_mock.return_value.query.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_context_predictor_tool_arun(
    prop, get_query_engine_mock, get_event_loop_mock
):
    tool = create_user_context_predictor_tool(**prop)
    await tool._arun("Hello")
    get_query_engine_mock.assert_called_once()
    get_event_loop_mock.assert_called_once()


def test_create_user_context_predictor_tool_error(prop):
    prop["index_dir"] = None
    with pytest.raises(ValueError) as e:
        create_user_context_predictor_tool(**prop)

    assert (
        str(e.value)
        == f"Config error : set 'llm_name' and 'index_dir' for tool {prop['name']}"
    )
