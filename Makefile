SHELL=/bin/bash

help:
	@echo 'Makefile for Some Fashion Group Catalog                                           '
	@echo '                                                                                  '
	@echo 'Usage:                                                                            '
	@echo '    make clean                                  Remove python compiled files      '
	@echo '    make requirements                           Install required packages         '
	@echo '    make requirements_dev                       Install required packages to Dev  '
	@echo '    make test                                   Run unit tests                    '
	@echo '    make test-matching Q=<Target Test>          Run specific unit tests           '
	@echo '    make coverage                               Run tests coverage                '
	@echo '    make lint                                   Check pep8 and imports            '
	@echo '    make run                                    Run the application               '
	@echo '    make containers                             Run container with mongo          '
	@echo '                                                                                  '


clean:
	find . -name "*.pyc" | xargs rm -rf
	find . -name "*.pyo" | xargs rm -rf
	find . -name "*.DS_Store" | xargs rm -rf
	find . -name "__pycache__" -type d | xargs rm -rf
	find . -name "*.cache" -type d | xargs rm -rf
	find . -name "*htmlcov" -type d | xargs rm -rf
	> errors.log > info.log
	rm -f .coverage
	rm -f coverage.xml

requirements:
	pip install -r requirements.txt

requirements_dev:
	pip install -r requirements_dev.txt

test:
	py.test -vv -s sfg_catalog

test-matching:
	py.test -rxs --pdb -k$(Q) sfg_catalog

coverage:
	py.test -xs --cov sfg_catalog --cov-report term-missing --cov-report xml sfg_catalog

lint:
	isort --check
	flake8 --exclude=venv

run:
	gunicorn sfg_catalog:app --bind localhost:8080 --worker-class aiohttp.worker.GunicornUVLoopWebWorker  --timeout=600

containers:
	docker-compose up -d