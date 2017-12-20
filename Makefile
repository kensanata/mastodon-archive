all:
	@echo "Have you edited setup.py?"
	@echo "Have you tagged the release?"
	@echo "Have you verified the User-Agent header in media.py?"

.PHONY: dist upload

dist:
	python3 setup.py sdist
	@echo make upload is next

upload:
	twine upload dist/*
