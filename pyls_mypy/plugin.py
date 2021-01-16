import re
import logging
import tempfile
from mypy import api as mypy_api
from pyls import hookimpl

line_pattern = r"([^:]+):(?:(\d+):)?(?:(\d+):)? (\w+): (.*)"

log = logging.getLogger(__name__)


def parse_line(line, document):
    """
    Return a language-server diagnostic from a line of the Mypy error report;
    optionally, use the whole document to provide more context on it.
    """
    result = re.match(line_pattern, line)
    if not result:
        return None

    file_path, lineno, offset, severity, msg = result.groups()
    if not document.path.endswith(file_path):
        log.warning("discarding result for %s against %s", file_path, document.path)
        return None

    lineno = int(lineno or 1) - 1  # 0-based line number
    offset = int(offset or 1) - 1  # 0-based offset
    start = {"line": lineno, "character": offset}

    # although mypy does not provide the end of the affected range, we
    # can make a good guess by highlighting the word that mypy flagged
    word = document.word_at_position(start)
    end = {
        "line": lineno,
        "character": offset + (len(word) if word else 1),
    }  # fallback to len of 1

    return {
        "source": "mypy",
        "range": {"start": start, "end": end},
        "message": msg,
        "severity": 1 if severity == "error" else 2,
    }


@hookimpl
def pyls_lint(config, workspace, document, is_saved):
    args = ["--no-pretty", "--show-column-numbers"]
    if is_saved:
        return execute_mypy(args + 1, document)

    with tempfile.NamedTemporaryFile("wt") as shadow_file:
        shadow_file.write(document.source)
        shadow_file.flush()

        return execute_mypy(
            args + ["--shadow-file", document.path, shadow_file.name], document
        )


def execute_mypy(args, document):
    report, errors, _ = mypy_api.run(args + [document.path])

    diagnostics = []
    for line in report.splitlines():
        diag = parse_line(line, document)
        if diag:
            diagnostics.append(diag)

    return diagnostics
