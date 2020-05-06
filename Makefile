PACKAGE := smart_path

all: 

push: format style-check test

test:
	pytest \
	    --cov=$(PACKAGE) \
	    --no-cov-on-fail \
	    --cov-report=html:htmlcov \
	    --cov-report term \
	    --doctest-modules \
	    $(PACKAGE) tests

format:
	autoflake -r -i $(PACKAGE) tests
	isort -rc $(PACKAGE) tests
	black $(PACKAGE) tests --line-length=120

style-check:
	black --diff --check $(PACKAGE) tests --line-length=120
	flake8 --ignore E501,E203,F401,W503,W504 --radon-max-cc 13 $(PACKAGE) tests
	mypy --ignore-missing-imports $(PACKAGE)

serve-coverage-report:
	cd htmlcov && python3 -m http.server

wheel:
	python3 setup.py sdist bdist_wheel
