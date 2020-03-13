
init:
	pipenv install -r requirements.txt

test:
	pipenv run py.test tests

.PHONY: init test
