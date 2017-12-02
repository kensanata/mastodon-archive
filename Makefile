all:
	@echo make dist is what you want

.PHONY: dist upload

dist:
	python3 setup.py sdist
	@echo make upload is next

upload:
	twine upload dist/*
