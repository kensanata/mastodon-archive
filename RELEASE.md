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

Note that the auth token for the upload is stored in ~/.pypirc

Push new tag to origin and github remotes!

Send a note to Izzy <izzy@qumran.org> for packaging `*.deb` and `*.rpm`.
Or use fedi: @IzzyOnDroid@floss.social.
