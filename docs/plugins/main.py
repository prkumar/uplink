import re
from pathlib import Path

from mkdocs.config import Config

THIS_DIR = Path(__file__).parent
DOCS_DIR = THIS_DIR.parent
PROJECT_ROOT = DOCS_DIR.parent


def on_pre_build(config: Config):
    """Before the build starts."""
    _add_changelog()


def _add_changelog() -> None:
    changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    changelog = re.sub(
        r"(\s)@([\w\-]+)", r"\1[@\2](https://github.com/\2)", changelog, flags=re.I
    )
    changelog = re.sub(
        r"\[GitHub release]\(", r"[:simple-github: GitHub release](", changelog
    )
    changelog = re.sub("@@", "@", changelog)
    new_file = DOCS_DIR / "changelog.md"

    # avoid writing file unless the content has changed to avoid infinite build loop
    if not new_file.is_file() or new_file.read_text(encoding="utf-8") != changelog:
        new_file.write_text(changelog, encoding="utf-8")
