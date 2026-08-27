PYTHON   := python3
VENV     := .venv
VENV_PIP := $(VENV)/bin/pip
PACKAGE  := src/std_works

PREFIX  ?= /usr/local
DESTDIR ?=
PYLIB   := $(shell $(PYTHON) -c 'import sys, sysconfig; print(sysconfig.get_path("purelib").replace(sys.prefix, "", 1).lstrip("/"))')

.PHONY: help venv install check run clean distclean

help:                    # default target
	@echo 'Targets:'
	@echo '  venv        distclean, then create .venv, then install the package editable'
	@echo '  install     copy the package (script, library, scriptures.sql) into PREFIX (default /usr/local); set DESTDIR to stage for packaging'
	@echo '  check       syntax-check the package and shim'
	@echo '  run         ./src/std-works ARGS="..." (bare `make run` opens the REPL)'
	@echo '  clean       remove build artifacts (keeps .venv)'
	@echo '  distclean   clean + remove .venv'

venv: distclean
	python3 -m venv $(VENV)
	$(VENV_PIP) install --editable .

install: check
	install -d $(DESTDIR)$(PREFIX)/bin $(DESTDIR)$(PREFIX)/$(PYLIB)
	printf '#!/usr/bin/python3\nimport sys, os\nsys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "$(PYLIB)"))\nfrom std_works.cli import main\nif __name__ == "__main__":\n    sys.exit(main())\n' \
	    > $(DESTDIR)$(PREFIX)/bin/std-works
	chmod 755 $(DESTDIR)$(PREFIX)/bin/std-works
	cp -r src/std_works $(DESTDIR)$(PREFIX)/$(PYLIB)/
	find $(DESTDIR)$(PREFIX)/$(PYLIB) -type d -name __pycache__ -prune -exec rm -rf {} +

check:
	$(PYTHON) -m py_compile $(PACKAGE)/*.py src/std-works

run:
	./src/std-works $(if $(ARGS),"$(ARGS)")

clean:
	rm -rf build dist src/Standard_Works.egg-info
	find src -type d -name __pycache__ -prune -exec rm -rf {} +

distclean: clean
	rm -rf $(VENV)