
init:
	python3 -m pipenv install --three -r requirements.txt

test:
	python3 -m pipenv run python setup.py test

.PHONY: init test
