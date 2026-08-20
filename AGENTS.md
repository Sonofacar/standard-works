# AGENTS.md

Python 3 rewrite of the LDS standard-works CLI (KJV Bible, Book of Mormon, D&C, Pearl of Great Price). Active branch is `python`; the original shell+awk+TSV implementation lives on `master` (its Makefile/TSV/awk rules do NOT apply here).

## Run

- Entry point is `src/std-works` (`#!/usr/bin/python3`). No build step — it runs in place: `./src/std-works "1 Nephi 3:7"`. The 2 MB `std-works` file at the repo root is a stale leftover binary from `master`; ignore it.
- There is no test target. `make` prints target help; `make venv` runs `distclean` then recreates `.venv` and installs the package editable; `make install` installs into `.venv` (auto-creating it if missing); `make check` syntax-checks the package and shim; `make run ARGS="..."` runs the CLI in place; `make clean` removes build artifacts (keeps `.venv`); `make distclean` also removes `.venv`. Nothing gates changes; verify manually.
- Flags differ from the shell version: `-p/--page` opens a pager (`pydoc.pager`, which invokes `less` with `-R`); `-c/--chars N` sets wrap width (default 70). `-s/--search TERM` searches all works (case-insensitive substring, no result limit) with optional `--work BOOK` scope (a book name or a `bible`/`bom`/`dc`/`pogp` table); a positional selection after the term also scopes the search. Search results print each match with its reference (`Book Chapter:Verse`) on its own line, then the verse text as normal, separated by blank lines, highlighting the term in yellow (highlight dropped when stdout is not a TTY, `NO_COLOR` set, or `TERM` is `dumb`); there is no results-count header. `-S/--list-search TERM` does the same search but prints only the references, one per line; `-s` and `-S` are mutually exclusive (using both is an error), and `-p` is ignored (with a warning to stderr) when `-S` is used. There is no "force cat" flag — pipe stdout instead.
- Queries are space-separated, colon only between chapter and verse: `"1 Nephi 3:7"`, not `"1 Nephi:3:7"`. Book names may be short (`1Ne`) or full (`1 Nephi`).
- With no args it launches an interactive REPL whose only verbs are `print/show`, `page/explore`, `search/find/grep` (trailing book name scopes the search), `list-search` (trailing book name scopes the search; references only), `help/?`, and `exit/quit/q/leave`. It has a built-in line editor (no readline): up/down recall history, left/right move the cursor, backspace edits.

## Layout

- `src/std_works/` package: `parse.py` turns a query string into a dict, `get.py` converts dicts to SQL and runs it against SQLite, `__init__.py` exports `parse`, `make_phrase`, `get_verses`, `print_verses` (also re-exports `re`).
- `src/std_works/scriptures.sql` is the only scripture data source — a tracked SQLite DB with tables `bible`, `bom`, `dc`, `pogp`, all `(indx, name, short_name, book_number, chapter, verse, text)`. It is generated data, not hand-edited.
- `scrape/` holds one-shot offline scrapers (requests + BeautifulSoup + pandas) that crawl churchofjesuschrist.org into SQLite artifacts; nothing wires them to the app or a build.
- `__pycache__/*.pyc` files are gitignored (none are tracked); `make clean` removes them.
- `setup.py` installs `std-works` as a `console_scripts` entry point (`std_works.cli:main`) with `package_data` carrying the `.sql`. Editable installs stay live because the CLI logic lives in the package; `src/std-works` is just a shim that calls `std_works.cli.main`.

## Quirks

- `get.py` builds SQL by string interpolation and resolves a book through `canonical_book()` (case-insensitive; `d&c`/`dc` alias to `DandC`) then `map_to_work()`. Unmatched books raise `ValueError`; ranges that are too long or span works raise `RuntimeError`/`ValueError`. The single-arg path catches these and prints `Error: <msg>` (exit 1); the REPL's bare `except` instead prints "Command not understood." Whole-book, whole-chapter, and chapter-range (`John 3-5`) queries are supported; `-c N` treats `N <= 0` as wrap width 1.
- pydoc and the REPL assume a TTY-friendly environment; don't rely on them under pipes.