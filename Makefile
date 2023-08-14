install:
	# install command
	pip install --upgrade pip &&\
		pip install -r requirements.txt

format:
	# format code
	black */*.py

lint:
	ruff check */*.py --fix
test:
	# test
	python -m pytest -vv tests/test_*.py

update-pre-commit:
	pre-commit autoupdate && pre-commit run --all-files && git commit -am 'updated linters / formatters'
pc:
	pre-commit run -a
build:
	# build container
	docker build -t deploy-fastapi .

run:
	# run docker
	docker run -p 127.0.0.1:8080 deploy-fastapi

deplpy:
	# deploy

all: install format test deploy
