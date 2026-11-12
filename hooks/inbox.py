"""Copy the InBox notes into the site so Copilot can read them on the web.

InBox/ stays the place notes are written. Before each build this hook copies its
Markdown files into docs/inbox/ (ignored by git); InBox/README.md becomes the
section's index page.
"""
import pathlib
import shutil


def on_pre_build(config, **kwargs):
    root = pathlib.Path(config["config_file_path"]).parent
    src = root / "InBox"
    dst = pathlib.Path(config["docs_dir"]) / "inbox"
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    for f in sorted(src.glob("*.md")):
        name = "index.md" if f.name.lower() == "readme.md" else f.name
        shutil.copyfile(f, dst / name)
