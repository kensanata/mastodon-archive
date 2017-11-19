# Mastodon Backup

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

    - [Making a backup](#making-a-backup)
    - [Generating a text file](#generating-a-text-file)
    - [Generating a HTML file](#generating-a-html-file)
    - [Documentation](#documentation)
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
authorization for this user and instance is stored. If these two files
exist, you don't have to log in the next time you run the application.

`dice.camp.user.kensanata.json` is the JSON file with your data (but
without your media attachments).

# Generating a text file

The tool `mastodon-backup-to-text.py` requires `html2text`:

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


# Generating a HTML file

You probably want to redirect the `mastodon-backup-to-text.py` output
to a file. Assuming you already made a backup of your toots:

```
$ ./mastodon-backup-to-html.py kensanata@dice.camp > kensanata.html
```

# Documentation

The data we have in our backup file is a hash with two keys:

1. `account` is a [User dict](https://mastodonpy.readthedocs.io/en/latest/#user-dicts)
2. `statuses` is a list of [Toot dicts](https://mastodonpy.readthedocs.io/en/latest/#toot-dicts)

If you want to understand the details and the nested nature of these
data structures, you need to look at the Mastodon API documentation.
One way to get started is to look at what a
[Status](https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#status)
entity looks like.

# Alternatives

There are two kinds of alternatives.

1. Solutions that extract your public toots from your profile, e.g.
   [https://octodon.social/@kensanata](https://octodon.social/@kensanata).
   The problem there is that you'll only get "top level" toots and
   boosts but *no replies*.
   
    * [Mastotool](https://mdhughes.tech/mastotool/) -- includes media
      download!
    * [MastoUserScrape.py](https://gist.github.com/FlyMyPG/2e9d4532453182ada0da78e74980193b)
   
2. Solutions that extract your public toots from your Atom feed, e.g.
   [https://octodon.social/users/kensanata.atom](https://octodon.social/users/kensanata.atom).
   The problem there is that you'll only get a few pages worth of
   toots, not *all* of them.

	* [Mastotool "Atom"](https://github.com/kensanata/mastotool)
