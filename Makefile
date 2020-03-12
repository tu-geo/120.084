
init:
	pipenv install -r requirements.txt

test:
	pipenv run python -m unittest discover tests

.PHONY: init test
