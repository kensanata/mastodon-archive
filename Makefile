all:
	@echo make dist is what you want

dist:
	python3 setup.py sdist
	@echo make upload is next

upload:
	twine upload dist/*
