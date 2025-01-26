all:
	@echo "Have you edited setup.py?"
	@echo "Have you verified the User-Agent header in media.py?"
	@echo "Have you tagged the release?"

.PHONY: dist upload

dist:
	python3 setup.py sdist
	@echo make upload is next

upload:
	twine upload --repository mastodon-archive dist/*
