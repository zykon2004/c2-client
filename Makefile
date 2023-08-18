install:
	# install command
	pip install --upgrade pip &&\
		pip install -r requirements.txt

format:
	# format code
	black */*.py

fmt: format

lint:
	ruff check */*.py --fix

update-pre-commit:
	pre-commit autoupdate && pre-commit run --all-files && git commit -am 'updated linters / formatters'

pc:
	pre-commit run -a
