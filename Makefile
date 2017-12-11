all:
	@echo "Have you edited setup.py?"
	@echo "Have you tagged the release?"

.PHONY: dist upload

dist:
	python3 setup.py sdist
	@echo make upload is next

upload:
	twine upload dist/*
