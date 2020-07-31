# .PHONY: test tox realthing guardduty clean

# docker:
# 	docker run --rm -it -v`pwd`:/work -w /work python:3.8 bash

# install: clean
# 	python setup.py install

# test-requirements:
# 	pip install -r tests/requirements.txt

lint:
	flake8 setup.py examples/ hclwriter/ tests/

test:
	PYTHONPATH=$(PWD) pytest -vv --cov=hclwriter tests/ && coverage report -m

tox:
	docker run --rm -it -v`pwd`:/work -w /work themattrix/tox

clean:
	rm -rf *.egg-info dist/ build/
	find . -type f -name '*.pyc' -delete
	find . -type d -name __pycache__ -delete
	# pip uninstall -y hclwriter



realthing:
	cd badoop/realthing \
		&& terraform destroy -auto-approve \
		&& ./realthing.py \
		&& terraform apply -parallelism=1 -auto-approve \
	;

guardduty:
	cd badoop/guardduty \
		&& ./guardduty.py \
		&& terraform fmt \
		&& terraform validate \
	;
