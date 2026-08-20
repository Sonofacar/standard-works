PYTHON   := python3
VENV     := .venv
VENV_PY  := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip
PACKAGE  := src/std_works

.PHONY: help venv install check run clean distclean

help:                    # default target
	@echo 'Targets:'
	@echo '  venv        distclean, then create .venv, then install the package'
	@echo '  install     install the package editable into .venv (creates it if missing)'
	@echo '  check       syntax-check the package and shim'
	@echo '  run         ./src/std-works ARGS="..." (bare `make run` opens the REPL)'
	@echo '  clean       remove build artifacts (keeps .venv)'
	@echo '  distclean   clean + remove .venv'

venv: distclean
	python3 -m venv $(VENV)
	$(VENV_PIP) install --editable .

install: $(VENV_PY)
	$(VENV_PIP) install --editable .

$(VENV_PY):
	python3 -m venv $(VENV)

check:
	$(PYTHON) -m py_compile $(PACKAGE)/*.py src/std-works

run:
	./src/std-works $(if $(ARGS),"$(ARGS)")

clean:
	rm -rf build dist src/Standard_Works.egg-info
	find src -type d -name __pycache__ -prune -exec rm -rf {} +

distclean: clean
	rm -rf $(VENV)