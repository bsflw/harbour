PYTHON   ?= python3
ENV_LOCATION = .env

all: setup test isort

test:
	# do nothing until I can get tests working :/
	# python -m unittest discover -v -s tests -p "*_test.py"

isort:
	isort -p harbour --skip .env -y

pr-prep: isort
	black --target-version py36 --exclude $(ENV_LOCATION) .

clean:
	-rm -r dist/ __pycache__/
	-rm -r packages/

setup: mk-venv
	/bin/bash $(ENV_LOCATION)/bin/activate && pip3 install -r requirements.txt
	@echo -e \\n-----------\\n\\nNow run 'source $(ENV_LOCATION)/bin/activate'

mk-venv:
	$(PYTHON) -m venv $(ENV_LOCATION)

rm-venv:
	rm -rf $(ENV_LOCATION)


.PHONY: all clean test isort mk-venv rm-venv setup
