# FMW Research

Research notes beside the [Federal Modernization Workbook](https://whalermike.github.io/modernization-workbook/).
**Not workbook guidance.**

Site: <https://whalermike.github.io/fmw-research/>

This project records questions about what cloud and service-management tools can do, with the
answers and their sources. It is kept apart from the workbook on purpose:

- Research may link to the workbook. The workbook never links to, imports or builds anything
  from this repository.
- No submodule, shared build or automation connects the two repositories.
- Every page is labelled as research, with a status and the date it was last checked.
- A finding joins the workbook only when the workbook owner names it and approves. It is then
  rewritten in a normal workbook pull request, not copied.

The full rules are on the site's [How this project works](docs/about.md) page.

## Layout

```
docs/
  index.md        home and topic list
  about.md        isolation rules, status values, integration path
  log.md          research log, newest first
  topics/         one page per research topic
  sources.md      every source used
mkdocs.yml        site configuration (MkDocs Material)
```

## Build locally

```bash
pip install mkdocs-material
mkdocs serve
```

## License

See [LICENSE.md](LICENSE.md). Writing: CC BY-NC-ND 4.0. Code: MIT.
