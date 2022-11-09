# Contrib
This directory contains user-provided contributions intended to enhance
mastodon-backup.

## `upgrade_python-mastodon.sh` (by Izzy)
A script intended to upgrade outdated versions of `Mastodon.py` when installed
via your Linux distribution's package manager. As of this writing,
mastodon-backup requires at least v1.5.1 for full functionality. It will
work with v1.5.0 with reduced functionality (e.g. bookmark operations are not
available). Some distributions ship even older versions. We explicitly decided
against requiring a specific version in the package's dependencies as that would
make the package unavailable for many LTS distributions, while the underlying
issue can easily be solved – by this script.

What it does:

* you call it from within this directory without any parameters
* it uses your package manager (`dpkg` or `yum`) to find out which version of
  `python3-mastodon` (DEB) or `python3-Mastodon` (RPM) is installed
* if it cannot find out (no `dpkg`/`yum` found or package not installed) it
  will inform you. You can then decide to proceed anyhow – or to use your
  package manager to install (this situation should not happen if you installed
  mastodon-backup via `apt`/`yum`, but who knows
* if a proper version (1.5.1 or later) was found, it says Good-Bye
* else it checks if the target directory & module exists. If not, it will abort.
* now it downloads the code from PyPi and replaces the existing old version
  located in `/usr/lib/python3/dist-packages/mastodon`.

Before any action takes place, you'll always be asked to confirm.

## `mastoarch` (by Izzy)
This is a wrapper for automation – intended to keep a close-to-complete copy
of your Mastodon account on your disk. Simply call it without parameters to
get details on its usage.

It will work in the directory you called it from. So if you wish to use it, I'd
recommend you either put it into your `$PATH` or create yourself an alias for it.

Once you've set it up and have it running, you could even have a Cron job
taken care for regular runs. Here I'd recommend the following command line:

```bash
cd /path/to/archive && mastoarch -a Me@MyInstance 2>/dev/null
```

If you've initialized a git repo with your archive, you could include `-g 1`
with the call to have changes committed automatically.

## `mastosearch` (by Izzy)
For your impromptu searches. Again a wrapper around the main script intended
to be easy to use. With your defaults set up in the configuration, a search
is as easy as `mastosearch <searchterm>`. Again, the full syntax is shown when
called without parameters.

## `config.sample` (by Izzy)
Lets you define defaults to use with `mastoarch` and `mastosearch` to make
calls to them as simple as possible. On your Linux machine, copy it to
`${HOME}/.config/mastodon-backup/config` and adjust it to fit your needs.
Hints inside.

## `mastodon-archive` (by Izzy)
`mastodon-archive` and `mastodon-archive.py` are wrapper scripts. The latter is
usually created automatically when installing via PyPi, the former is intended
to go to `/usr/bin` (or somewhere else in your `$PATH`). Both are used with the
DEB/RPM packages maintained by me.
