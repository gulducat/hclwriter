# docker:
# 	docker run --rm -it -v`pwd`:/work -w /work python:3.8 bash

# install: clean
# 	python setup.py install

# test-requirements:
# 	pip install -r tests/requirements.txt

default: lint test

lint:
	flake8 setup.py examples/ hclwriter/ tests/

test:
	PYTHONPATH=$(PWD) pytest -v --cov=hclwriter tests/

tox:
	docker run --rm -it -v`pwd`:/work -w /work themattrix/tox

build:
	pip install setuptools wheel
	python setup.py sdist bdist_wheel

clean:
	rm -rf .coverage .pytest_cache/ dist/ build/ *.egg-info/
	find . -type f -name '*.pyc' -delete
	find . -type d -name __pycache__ -delete
	pip uninstall -y hclwriter

.PHONY: default lint test tox clean
