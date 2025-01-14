import pytest
from mock import Mock

from pyls import uris
from pyls.config.config import Config
from pyls.workspace import Document, Workspace
from pyls_mypy import plugin

DOC_URI = uris.from_fs_path(__file__)
DOC = """{}.append(3)
"""

TYPE_ERR_MSG = '"Dict[<nothing>, <nothing>]" has no attribute "append"'

TEST_LINE = 'test_plugin.py:279:8: error: "Request" has no attribute "id"'
TEST_LINE_WITHOUT_COL = "test_plugin.py:279: " 'error: "Request" has no attribute "id"'
TEST_LINE_WITHOUT_LINE = "test_plugin.py: " 'error: "Request" has no attribute "id"'


@pytest.fixture
def workspace(tmpdir):
    """Return a workspace."""
    ws = Workspace(uris.from_fs_path(str(tmpdir)), Mock())
    ws._config = Config(ws.root_uri, {}, 0, {})
    return ws


@pytest.fixture
def config(workspace):
    """Return a workspace."""
    return Config(workspace.root_uri, {}, 0, {})


def test_plugin(config, workspace):
    doc = Document(DOC_URI, workspace, DOC)
    diags = plugin.pyls_lint(config, workspace, doc, is_saved=False)

    assert len(diags) == 1
    diag = diags[0]
    assert diag["message"] == TYPE_ERR_MSG
    assert diag["range"]["start"] == {"line": 0, "character": 0}
    assert diag["range"]["end"] == {"line": 0, "character": 1}


def test_parse_full_line(workspace):
    doc = Document(DOC_URI, workspace, DOC)
    diag = plugin.parse_line(TEST_LINE, doc)
    assert diag["message"] == '"Request" has no attribute "id"'
    assert diag["range"]["start"] == {"line": 278, "character": 7}
    assert diag["range"]["end"] == {"line": 278, "character": 8}


def test_parse_line_without_col(workspace):
    doc = Document(DOC_URI, workspace, DOC)
    diag = plugin.parse_line(TEST_LINE_WITHOUT_COL, doc)
    assert diag["message"] == '"Request" has no attribute "id"'
    assert diag["range"]["start"] == {"line": 278, "character": 0}
    assert diag["range"]["end"] == {"line": 278, "character": 1}


def test_parse_line_without_line(workspace):
    doc = Document(DOC_URI, workspace, DOC)
    diag = plugin.parse_line(TEST_LINE_WITHOUT_LINE, doc)
    assert diag["message"] == '"Request" has no attribute "id"'
    assert diag["range"]["start"] == {"line": 0, "character": 0}
    assert diag["range"]["end"] == {"line": 0, "character": 1}


@pytest.mark.parametrize("word,bounds", [("", (7, 8)), ("my_var", (7, 13))])
def test_parse_line_with_context(workspace, monkeypatch, word, bounds):
    doc = Document(DOC_URI, workspace, DOC)
    monkeypatch.setattr(Document, "word_at_position", lambda *args: word)
    diag = plugin.parse_line(TEST_LINE, doc)
    assert diag["message"] == '"Request" has no attribute "id"'
    assert diag["range"]["start"] == {"line": 278, "character": bounds[0]}
    assert diag["range"]["end"] == {"line": 278, "character": bounds[1]}
