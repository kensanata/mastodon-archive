# Mastodon Backup

This tool allows you to make a backup of your statuses, your
favourites and the media in both your statuses and your favourites.
From this backup, you can generate a simple text file, or a HTML file
with or without media. Take a look at an
[example](https://alexschroeder.ch/mastodon.weaponvsac.space.user.kensanata.html)
if you're curious.

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Making a backup](#making-a-backup)
- [Downloading media files](#downloading-media-files)
- [Generating a text file](#generating-a-text-file)
- [Searching your backup](#searching-your-backup)
- [Generating a HTML file](#generating-a-html-file)
- [Documentation](#documentation)
- [Processing using jq](#processing-using-jq)
- [Alternatives](#alternatives)

<!-- markdown-toc end -->

# Making a backup

This tool uses the [Mastodon.py](https://github.com/halcy/Mastodon.py)
library which you must install:

```bash
# Python 3
pip3 install Mastodon.py
```

When using the app for the first time, you will have to authorize it:

```
$ ./mastodon-backup.py kensanata@dice.camp
Registering app
Log in
Visit the following URL and authorize the app:
[the app gives you a huge URL which you need to visit using a browser]
Then paste the access token here:
[this is where you paste the authorization code]
Get user info
Get statuses (this may take a while)
Save 41 statuses
```

You will end up with three new files:

`dice.camp.client.secret` is where the client secret for this instance
is stored. `dice.camp.user.kensanata.secret` is where the
authorisation for this user and instance is stored. If these two files
exist, you don't have to log in the next time you run the application.

`dice.camp.user.kensanata.json` is the JSON file with your data (but
without your media attachments).

# Downloading media files

By default, media you uploaded and media of statuses you added your
favourites are not part of your backup. `mastodon-backup-media.py`
will look through your backup and download all the missing media
files.

It requires [progress](https://pypi.python.org/pypi/progress)
and [pySmartDL](https://pypi.python.org/pypi/pySmartDL):

```bash
# Python 3
pip3 install pySmartDL
pip3 install progress
```

Assuming you already made a backup of your toots:

```
$ ./mastodon-backup-media.py kensanata@dice.camp
44 urls in your backup (half of them are previews)
34 files already exist
Downloading |################################| 10/10
```

You will end up with a new directory, `dice.camp.user.kensanata`. It
contains all the media you uploaded, and their corresponding previews.

If you rerun it, it will simply try to get the remaining files. Note,
however, that instance administrators can *delete* media files. Thus,
you might be forever missing some files—particularly the ones from
*remote* instances, if you added any to your favourites.

There's one thing you need to remember, though: the media directory
contains all the media from your statuses, and all the media from your
favourites. There is no a particular reason why the media files from
both sources need to be in the same directory. If you think this is a
problem, [create an issue](https://github.com/kensanata/mastodon-backup/issues)
and we'll discuss it.

# Generating a text file

The tool `mastodon-backup-to-text.py` requires
[html2text](https://pypi.python.org/pypi/html2text):

```bash
# Python 3
pip3 install html2text
```

Assuming you already made a backup of your toots:

```
$ ./mastodon-backup-to-text.py kensanata@dice.camp
[lots of other toots]
Alex Schroeder 🐉 @kensanata 2017-11-14T22:21:50.599000+00:00
[#introduction](https://dice.camp/tags/introduction) I run
[#osr](https://dice.camp/tags/osr) games using my own hose rule document but
it all started with Labyrinth Lord which I knew long before I knew B/X. Sadly,
my Indie Game Night is no longer a thing but I still love Lady Blackbird, all
the [#pbta](https://dice.camp/tags/pbta) hacks on my drive, and so much more.
But in the three campaigns I run, it’s all OSR right now.
```

Generating a text file just means redirection the output to a text
file:

```
$ ./mastodon-backup-to-text.py kensanata@dice.camp > statuses.txt
```

# Searching your backup

You can also filter using regular expressions. These will be checked
against the status *content* (obviously), *display name* and
*username* (both are important for boosted toots), and the *created
at* date. Also note that the regular expression will be applied to the
raw status content. In other words, the status contains all the HTML
and problably starts with a `<p>`, which is then removed in the
output.

```
$ ./mastodon-backup-to-text.py kensanata@dice.camp house
```

You can provide multiple regular expressions and they will all be
checked:

```
$ ./mastodon-backup-to-text.py kensanata@dice.camp house rule
```

Remember basic
[regular expression syntax](https://docs.python.org/3/library/re.html#regular-expression-syntax):
`\b` is a word boundary, `(?i)` ignores case, `(a|b)` is for
alternatives, just to pick some useful ones. Use single quotes to
protect your backslashes and questionmarks.

```
$ ./mastodon-backup-to-text.py kensanata@dice.camp house 'rule\b'
```

You can also search your favourites:

```
$ ./mastodon-backup-to-text.py favourites kensanata@dice.camp '(?i)blackbird'
```

Dates are in ISO format (e.g. `2017-11-19T14:00`). I usually only care
about year and month, though:

```
$ ./mastodon-backup-to-text.py favourites kensanata@dice.camp bird '2017-(07|08|09|10|11)'
```

# Generating a HTML file

You probably want to redirect the `mastodon-backup-to-text.py` output
to a file. Assuming you already made a backup of your toots:

```
$ ./mastodon-backup-to-html.py kensanata@dice.camp > statuses.html
```

If you have downloaded your media attachments, these will be used in
the HTML file. Thus, if you want to upload the HTML file, you now need
to upload the media directory as well or all the media links will be
broken.

You can also generate a file for your favourites:

```
$ ./mastodon-backup-to-html.py favourites kensanata@dice.camp > favourites.html
```

Note that both the HTML file with your statuses and the HTML file with
your favourites will refer to the media files in your media directory.

# Documentation

The data we have in our backup file is a hash with two keys:

1. `account` is a [User dict](https://mastodonpy.readthedocs.io/en/latest/#user-dicts)
2. `statuses` is a list of [Toot dicts](https://mastodonpy.readthedocs.io/en/latest/#toot-dicts)

If you want to understand the details and the nested nature of these
data structures, you need to look at the Mastodon API documentation.
One way to get started is to look at what a
[Status](https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#status)
entity looks like.

# Processing using jq

[jq](https://stedolan.github.io/jq/) is a lightweight and flexible
command-line JSON processor. That means you can use it to work with
your backup.

The following command will take all your favourites and create a map
with the keys `time` and `message` for each one of them, and put it
all in an array.

```
$ jq '[.favourites[] | {time: .account.username, message: .content}]' < dice.camp.user.kensanata.json
```

Example output, assuming I had only a single favourite:

```
[
  {
    "time": "andrhia",
    "message": "<p>It’s nice to reinvent yourself every so often, don’t you think?</p>"
  }
]
```

# Alternatives

There are two kinds of alternatives to `mastodon-backup`:

1. Solutions that extract your public toots from your profile, e.g.
   [https://octodon.social/@kensanata](https://octodon.social/@kensanata).
   The problem there is that you'll only get "top level" toots and
   boosts but *no replies*.
   
    * [Mastotool](https://mdhughes.tech/mastotool/) includes media
      download!
    * [MastoUserScrape.py](https://gist.github.com/FlyMyPG/2e9d4532453182ada0da78e74980193b)
   
2. Solutions that extract your public toots from your Atom feed, e.g.
   [https://octodon.social/users/kensanata.atom](https://octodon.social/users/kensanata.atom).
   The problem there is that you'll only get a few pages worth of
   toots, not *all* of them.

	* [Mastotool "Atom"](https://github.com/kensanata/mastotool)
