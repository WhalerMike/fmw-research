"""Build the sandbox packs zip into the site on every build.

The zip is served from the site itself (downloads/fmw-sandbox-packs.zip), so it can
be downloaded where GitHub is blocked and always matches the pages. Links between
files are rewritten to site addresses, and each file starts with its own address.
"""
import pathlib
import posixpath
import re
import zipfile

BASE = "https://whalermike.github.io/fmw-research/"
ZIP_NAME = "fmw-sandbox-packs.zip"
FOLDER = "fmw-sandbox-packs"


def _url(page):  # page like "sandbox/pack-1-x.md" or "sandbox/index.md"
    page = page[:-3]
    page = page[:-5] if page.endswith("index") else page + "/"
    return BASE + page


def _rewrite(text, page_dir):
    def rep(m):
        label, link = m.group(1), m.group(2)
        if re.match(r"[a-z]+:", link) or link.startswith("#"):
            return m.group(0)
        path, _, frag = link.partition("#")
        url = _url(posixpath.normpath(posixpath.join(page_dir, path)))
        return f"[{label}]({url}{'#' + frag if frag else ''})"

    text = re.sub(r"\{ ?\.md-button[^}]*\}", "", text)  # site-only button styling
    text = re.sub(r":material-[a-z-]+: ?", "", text)  # site-only icons
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", rep, text)


def _with_address(text, url):
    first, _, rest = text.partition("\n")
    return f"{first}\n\nOnline version: <{url}>\n{rest}"


README = """FMW Research - ServiceNow sandbox test packs

Research notes, not Federal Modernization Workbook guidance.
Steps are drafts until a sandbox run confirms them; menu names and APIs differ by ServiceNow release.

Every link in these files points to the research website, not to GitHub,
so Copilot or a browser inside the work environment can open them.

Start here
{start}

Run the packs in order, then record each run in a copy of the results template
{packs}

Keep filled-in results on work storage. Only the generic finding at the end of the
template leaves work, retyped by hand.

Website: {base}
Latest copy of this zip: {base}downloads/{zip}
License: writing CC BY-NC-ND 4.0; commands and code blocks MIT. See LICENSE.md.
"""


def on_post_build(config, **kwargs):
    root = pathlib.Path(config["config_file_path"]).parent
    docs = pathlib.Path(config["docs_dir"])
    files = []  # (name in zip, text, url)

    for f in sorted((root / "InBox").glob("[0-9]*.md")):
        url = _url("inbox/" + f.name)
        text = _rewrite(f.read_text(encoding="utf-8"), "inbox")
        files.append((f.name, _with_address(text, url), url))

    for f in sorted((docs / "sandbox").glob("*.md")):
        name = "README-overview.md" if f.name == "index.md" else f.name
        url = _url("sandbox/" + f.name)
        text = _rewrite(f.read_text(encoding="utf-8"), "sandbox")
        files.append((name, _with_address(text, url), url))

    start = [n for n in files if n[0][0].isdigit() or n[0] == "README-overview.md"]
    packs = [n for n in files if n not in start]
    line = lambda n: f"  {n[0]:40} {n[2]}"
    readme = README.format(
        start="\n".join(map(line, start)),
        packs="\n".join(map(line, packs)),
        base=BASE,
        zip=ZIP_NAME,
    )

    out = pathlib.Path(config["site_dir"]) / "downloads"
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out / ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"{FOLDER}/README.txt", readme)
        z.write(root / "LICENSE.md", f"{FOLDER}/LICENSE.md")
        for name, text, _ in files:
            z.writestr(f"{FOLDER}/{name}", text)
