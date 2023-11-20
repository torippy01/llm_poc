import pytest

import llama_index
from xecretary_core.context_fetcher import github_wiki


@pytest.fixture
def wiki_url():
    return "https://github.com/torippy01/llm_poc/wiki/_Footer"


def test_trim_owner(wiki_url):
    assert github_wiki.trim_owner(wiki_url) == "torippy01"


def test_trim_repo(wiki_url):
    assert github_wiki.trim_repo(wiki_url) == "llm_poc"


def test_github_wiki(mocker, wiki_url):
    # 依存パッケージ類のモック
    mocker.patch("git.repo.base.Repo.clone_from")
    mocker.patch("shutil.rmtree")

    # SimpleDirectoryReaderのインスタンスのMagicMock
    simple_directory_reader_magic_mock = mocker.MagicMock(
        spec=llama_index.SimpleDirectoryReader
    )
    mocker.patch(
        "xecretary_core.context_fetcher.github_wiki.SimpleDirectoryReader",
        return_value=simple_directory_reader_magic_mock,
    )

    # class method、from_documentsのモック
    from_documents_mock = mocker.patch.object(
        llama_index.GPTVectorStoreIndex, "from_documents"
    )

    github_wiki_instance = github_wiki.GithubWiki(wiki_url)

    assert (
        github_wiki_instance.repo_url == "https://github.com/torippy01/llm_poc.wiki.git"
    )
    assert github_wiki_instance.index_id == "torippy01.llm_poc"
    assert github_wiki_instance.tmp_url == "tmp/torippy01.llm_poc"

    github_wiki_instance.create_index()

    # load_dataメソッドが一度だけよばれたか
    simple_directory_reader_magic_mock.load_data.assert_called_once()

    # from_documentsメソッドが一度だけよばれたか
    from_documents_mock.assert_called_once()

    # set_index_idメソッドが一度だけよばれたか
    from_documents_mock().set_index_id.assert_called_once()

    # persistメソッドが一度だけ呼ばれたか
    from_documents_mock().storage_context.persist.assert_called_once()
