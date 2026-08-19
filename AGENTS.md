# AGENTS.md

Python 3 rewrite of the LDS standard-works CLI (KJV Bible, Book of Mormon, D&C, Pearl of Great Price). Active branch is `python`; the original shell+awk+TSV implementation lives on `master` (its Makefile/TSV/awk rules do NOT apply here).

## Run

- Entry point is `src/std-works` (`#!/usr/bin/python3`). No build step — it runs in place: `./src/std-works "1 Nephi 3:7"`. The 2 MB `std-works` file at the repo root is a stale leftover binary from `master`; ignore it.
- There is no Makefile and no test target on this branch. Nothing gates changes; verify manually.
- Flags differ from the shell version: `-p/--page` opens a pager (`pydoc.pager`); `-c/--chars N` sets wrap width (default 70). There is no "force cat" flag — pipe stdout instead.
- Queries are space-separated, colon only between chapter and verse: `"1 Nephi 3:7"`, not `"1 Nephi:3:7"`. Book names may be short (`1Ne`) or full (`1 Nephi`).
- With no args it launches an interactive REPL whose only working verbs are `print/show`, `page/explore`, `help/?`, and `exit/quit/q/leave`. `query`/`search`/`list`/`add` are in the `verbs` table but have no `do_command` case — using one makes the REPL exit silently.

## Layout

- `src/std_works/` package: `parse.py` turns a query string into a dict, `get.py` converts dicts to SQL and runs it against SQLite, `__init__.py` exports `parse`, `make_phrase`, `get_verses`, `print_verses` (also re-exports `re`).
- `src/std_works/scriptures.sql` is the only scripture data source — a tracked SQLite DB with tables `bible`, `bom`, `dc`, `pogp`, all `(indx, name, short_name, book_number, chapter, verse, text)`. It is generated data, not hand-edited.
- `scrape/` holds one-shot offline scrapers (requests + BeautifulSoup + pandas) that crawl churchofjesuschrist.org into SQLite artifacts; nothing wires them to the app or a build.
- Committed `__pycache__/*.pyc` files are tracked in git, including stale pyc for deleted `notes.py`/`print_verses.py`; don't add more.
- `setup.py` installs `std-works` as a `console_scripts` entry point (`std_works.cli:main`) with `package_data` carrying the `.sql`. Editable installs stay live because the CLI logic lives in the package; `src/std-works` is just a shim that calls `std_works.cli.main`.

## Quirks

- `get.py` builds SQL by string interpolation and resolves a book through `map_to_work()` against hardcoded `bible`/`bom`/`dc`/`pogp` name lists. An unmatched book returns `'error'`, producing `SELECT ... FROM error` and an unhandled `sqlite3.OperationalError` traceback (the single-arg path has no try/except; the REPL's bare `except` instead prints "Command not understood.")
- pydoc and the REPL assume a TTY-friendly environment; don't rely on them under pipes.