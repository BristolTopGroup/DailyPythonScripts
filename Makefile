PYTHON := $(shell which python)
NOSETESTS := $(shell which nosetests)

INTERACTIVE := $(shell ([ -t 0 ] && echo 1) || echo 0)                          
                                                                                
UNAME_S := $(shell uname -s)                                                    
ifeq ($(UNAME_S),Darwin)                                                        
        OPEN := open                                                            
else                                                                            
        OPEN := xdg-open                                                        
endif

.PHONY: clean-pyc clean-build docs

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "sdist - package"

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

inplace:
	@$(PYTHON) setup.py build_ext -i

lint:
	flake8 src tools

test-code:
	@$(NOSETESTS) -v -a '!slow' -s .

test: test-code

coverage:
	@rm -rf coverage .coverage
	@$(NOSETESTS) -s -v -a '!slow' --with-coverage \
		--cover-erase --cover-branches \
		--cover-html --cover-html-dir=coverage src tools
	@if [ "$(INTERACTIVE)" -eq "1" ]; then \
		$(OPEN) coverage/index.html; \
	fi

docs:
	rm -f docs/dps.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ src tools
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(OPEN) docs/_build/html/index.html

release: clean
	python setup.py sdist upload

sdist: clean
	python setup.py sdist
	ls -l dist
	
