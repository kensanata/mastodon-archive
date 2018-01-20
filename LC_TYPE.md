# Locale

Sometimes you'll get an error relating to your locale.

You can fix your setup by adding a statement to your shell's init
file. The following is supposed to set a bunch of similar settings at
the same time for future terminal settings.

```
echo export LANG=en_US.UTF-8 >> ~/.bashrc
```

Why does it work? Starting at the end:

1. `>> ~/.bashrc` appends a line to your shell's init file, and
   usually the default shell in terminals is `bash` which uses
   `~/.bashrc` as its init file
2. `en_US.UTF-8` means that you want English/US settings and UTF-8
   encoded output
3. `LANG` is the environment variable that controls all of this, more
   on that below
4. `export` means that it work in the current shell, and all other
   programs it calls (such as `mastodon-archive`)
5. `echo` simply prints the line `export LANG=en_US.UTF-8` such that
   `>> ~/.bashrc` will append it to the `~/.bashrc` file

I promised some more information about your settings. Use the `locale`
command to determine your current settings:

```
$ locale
LANG=
LC_COLLATE="C"
LC_CTYPE="UTF-8"
LC_MESSAGES="C"
LC_MONETARY="C"
LC_NUMERIC="C"
LC_TIME="C"
LC_ALL=
```

See how it changes when you set `LANG`:

```
$ export LANG=en_US.UTF-8
$ locale
LANG="en_US.UTF-8"
LC_COLLATE="en_US.UTF-8"
LC_CTYPE="UTF-8"
LC_MESSAGES="en_US.UTF-8"
LC_MONETARY="en_US.UTF-8"
LC_NUMERIC="en_US.UTF-8"
LC_TIME="en_US.UTF-8"
LC_ALL=
```
