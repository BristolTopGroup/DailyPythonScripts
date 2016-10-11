# simple makefile to simplify repetitive build env management tasks under posix

PYTHON := $(shell which python)
NOSETESTS := $(shell which nosetests)

INTERACTIVE := $(shell ([ -t 0 ] && echo 1) || echo 0)                          
                                                                                
UNAME_S := $(shell uname -s)
PROJECT_NAME := dps

                                               
ifeq ($(UNAME_S),Darwin)                                                        
        OPEN := open                                                            
else                                                                            
        OPEN := xdg-open                                                        
endif

all: clean inplace test

# list what would be deleted by clean-repo
clean-repo-check:
	@git clean -f -x -d -n

clean-dict:
	@rm -f AutoDict_*

clean-pyc:
	@find . -name "*.pyc" -exec rm {} \;
	
clean-so:
	@find $(PROJECT_NAME) -name "*.so" -exec rm {} \;

clean-build:
	@rm -rf build

clean-dist:
	@rm -fr dist
	@rm -fr $(PROJECT_NAME).egg-info

clean: clean-build clean-pyc clean-so clean-dict clean-dist

in: inplace # just a shortcut
inplace:
	@$(PYTHON) setup.py build_ext -i

install: clean
	@$(PYTHON) setup.py install

install-user: clean
	@$(PYTHON) setup.py install --user

sdist: clean
	@$(PYTHON) setup.py sdist --release

register:
	@$(PYTHON) setup.py register --release

upload: clean
	@$(PYTHON) setup.py sdist upload --release

test-code: inplace
	@$(NOSETESTS) -v -a '!slow' -s tests

test-code-full: inplace
	@$(NOSETESTS) -v -s tests

test-code-verbose: inplace
	@$(NOSETESTS) -v -a '!slow' -s tests --nologcapture

test-installed:
	@(mkdir -p nose && cd nose && \
	$(NOSETESTS) -v -a '!slow' -s --exe tests && \
	cd .. && rm -rf nose)

test-doc:
	@$(NOSETESTS) -v -s --with-doctest --doctest-tests --doctest-extension=rst \
	--doctest-extension=inc --doctest-fixtures=_fixture docs/

test-coverage:
	@rm -rf coverage .coverage
	@$(NOSETESTS) -s -v -a '!slow' --with-coverage \
		--cover-erase --cover-branches \
		--cover-html --cover-html-dir=coverage rootpy
	@if [ "$(INTERACTIVE)" -eq "1" ]; then \
		$(OPEN) coverage/index.html; \
	fi;

test: test-code

trailing-spaces:
	@find $(PROJECT_NAME) -name "*.py" | xargs perl -pi -e 's/[ \t]*$$//'

doc: inplace
	@make -C docs/ html

check-rst:
	@mkdir -p build
	@$(PYTHON) setup.py --long-description | rst2html.py > build/README.html
	@$(OPEN) build/README.html

pep8:
	@pep8 --exclude=.git,extern $(PROJECT_NAME)

flakes:
	@./ci/run-pyflakes
