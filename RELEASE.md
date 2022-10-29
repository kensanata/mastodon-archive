# How to make a release

Increase the version number in setup.py.

Tag the commit.

```
make dist
```

Possibly clean up the dist/ folder.

```
make upload
```

Push new tag to origin and github remotes!
