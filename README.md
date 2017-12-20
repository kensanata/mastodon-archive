# Mastodon Archive

This tool allows you to make an archive of your statuses, your
favourites and the media in both your statuses and your favourites.
From this archive, you can generate a simple text file, or a HTML file
with or without media. Take a look at an
[example](https://alexschroeder.ch/mastodon.weaponvsac.space.user.kensanata.html)
if you're curious.

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Installation](#installation)
- [Making an archive](#making-an-archive)
- [Downloading media files](#downloading-media-files)
- [Generating a text file](#generating-a-text-file)
- [Searching your archive](#searching-your-archive)
- [Generating a HTML file](#generating-a-html-file)
- [Reporting](#reporting)
- [Expiring your toots and favourites](#expiring-your-toots-and-favourites)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)
- [Development](#development)
- [Processing using jq](#processing-using-jq)
- [Exploring the API](#exploring-the-api)
- [Alternatives](#alternatives)

<!-- markdown-toc end -->

# Installation

The following command will install `mastodon-archive` and all its
dependencies:

```bash
# Python 3
$ pip3 install mastodon-archive
```

# Making an archive

When using the app for the first time, you will have to authorize it:

```
$ mastodon-archive archive kensanata@dice.camp
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

Note that the library we are using says: "Mastodons API rate limits
per IP. By default, the limit is 300 requests per 5 minute time slot.
This can differ from instance to instance and is subject to change."
Thus, if every request gets 20 toots, then we can get at most 6000
toots per five minutes.

If this is taking too long, consider skipping your favourites:

```
$ mastodon-archive archive --no-favourites kensanata@dice.camp
```

You will end up with three new files:

`dice.camp.client.secret` is where the client secret for this instance
is stored. `dice.camp.user.kensanata.secret` is where the
authorisation token for this user and instance is stored. If these two
files exist, you don't have to log in the next time you run the app.
If your login expired, you need to remove the file containing the
authorisation token and you will be asked to authorize the app again.

`dice.camp.user.kensanata.json` is the JSON file with your data (but
without your media attachments). If this file exists, only the missing
toots will be downloaded the next time you run the app. If you suspect
a problem and want to make sure that everything is downloaded again,
you need to remove this file.

# Downloading media files

By default, media you uploaded and media of statuses you added your
favourites are not part of your archive. You can download it using a
separate command, however.

Assuming you already made an archive of your toots:

```
$ mastodon-archive media kensanata@dice.camp
44 urls in your archive (half of them are previews)
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
favourites. There is no particular reason why the media files from
both sources need to be in the same directory, see
[issue #11](https://github.com/kensanata/mastodon-backup/issues/11).

# Generating a text file

Assuming you already made an archive of your toots:

```
$ mastodon-archive text kensanata@dice.camp
[lots of other toots]
Alex Schroeder 🐉 @kensanata 2017-11-14T22:21:50.599000+00:00
https://dice.camp/@kensanata/99005111284322450
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
$ mastodon-archive text kensanata@dice.camp > statuses.txt
```

If you're working with text, you might expect the first toot to be at
the top and the last toot to be at the bottom. In this case, you need
to reverse the list:

```
$ mastodon-archive text --reverse kensanata@dice.camp | head
```

# Searching your archive

You can also filter using regular expressions. These will be checked
against the status *content* (obviously), *display name* and
*username* (both are important for boosted toots), and the *created
at* date. Also note that the regular expression will be applied to the
raw status content. In other words, the status contains all the HTML
and problably starts with a `<p>`, which is then removed in the
output.

```
$ mastodon-archive text kensanata@dice.camp house
```

You can provide multiple regular expressions and they will all be
checked:

```
$ mastodon-archive text kensanata@dice.camp house rule
```

Remember basic
[regular expression syntax](https://docs.python.org/3/library/re.html#regular-expression-syntax):
`\b` is a word boundary, `(?i)` ignores case, `(a|b)` is for
alternatives, just to pick some useful ones. Use single quotes to
protect your backslashes and questionmarks.

```
$ mastodon-archive text kensanata@dice.camp house 'rule\b'
```

You can also search your favourites:

```
$ mastodon-archive text --collection favourites kensanata@dice.camp '(?i)blackbird'
```

Dates are in ISO format (e.g. `2017-11-19T14:00`). I usually only care
about year and month, though:

```
$ mastodon-archive text --collection favourites kensanata@dice.camp bird '2017-(07|08|09|10|11)'
```

# Generating a HTML file

Assuming you already made an archive of your toots:

```
$ mastodon-archive html kensanata@dice.camp
```

This will create numbered HTML files starting with
`dice.camp.user.kensanata.statuses.0.html`, each page with 2000 toots.

You can change the number of toots per page using an option:

```
$ mastodon-archive html --toots-per-page 100 kensanata@dice.camp
```

If you have downloaded your media attachments, these will be used in
the HTML files. Thus, if you want to upload the HTML files, you now
need to upload the media directory as well or all the media links will
be broken.

You can also generate a file for your favourites:

```
$ mastodon-archive html --collection favourites kensanata@dice.camp
```

This will create numbered HTML files starting with
`dice.camp.user.kensanata.favourites.0.html`, each page with 2000
toots.

Note that both the HTML file with your statuses and the HTML file with
your favourites will refer to the media files in your media directory.

# Reporting

Some numbers, including your ten most used hashtags:

```
$ mastodon-archive report kensanata@dice.camp
Statuses:               209
Boosts:                  14
Media:                    5
Favourites:             223

#caster(5) #20questions(5) #introduction(2) #osr(2)
#currentprojects(2) #caller(1) #rpgmusic(1) #razorcoast(1)
#rpghaiku(1) #haiku(1) #character(1) #amaroq(1) #tootdon(1) #howto(1)
#spells(1) #history(1) #rpg(1) #myfirstcharacter(1) #1strpgs(1)
#favouritepen(1) #pbta(1)
```

# Expiring your toots and favourites

**Warning**: This is a destructive operation. You will delete your
toots on your instance, or unfavour your favourites on your instance.
Where as it might be possible to favour all your favourites again,
there is no way to repost all those toots. You will have a copy in
your archive, but there is no way to restore these to your instance.

You can expire your toots using the `expire` command and providing the
`--older-than` option. This option specifies the number of weeks to
keep on the server. Anything older than that is deleted or unfavoured.
If you use `--older-than 0`, then *all* your toots will be deleted or
*all* your favourites will be unfavoured.

```
~/src/mastodon-backup $ mastodon-archive expire --older-than 0 kensanata@social.nasqueron.org
This is a dry run and nothing will be expired.
Instead, we'll just list what would have happened.
Use --confirmed to actually do it.
Delete: 2017-11-26 "<p>Testing äöü</p>"
```

Actually, the default operation just does a dry run. You need to use
the `--confirmed` option to proceed.

And one more thing: since this requires the permission to *write* to
your account, you will have to reauthorize the app.

```
$ mastodon-archive expire --collection favourites --older-than 0 \
  --confirmed kensanata@social.nasqueron.org
Log in
Visit the following URL and authorize the app:
[long URL shown here]
Then paste the access token here:
[long token pasted here]
Expiring |################################| 1/1
```

These toots will remain in your archive. And now you have a problem if
you deleted *all* the toots from your instance using `--older-than 0`
because when you try to archive your toots a while later, the app will
attempt to fetch toots up to the last one in your archive, but you
deleted it, so it can't be found.

```
$ mastodon-archive archive kensanata@social.nasqueron.org
Loading existing archive
Get user info
Get new statuses
Error: I did not find the last toot we have in our archive.
Perhaps it was deleted?

If you have expired all the toots on your server, then this is
expected. In this case you need to use the --append-all option to make
sure we download all the toots on the server and append them to the
archive.

If you have never expired any toots and you just manually deleted or
unfavoured the last one in the archive, you could first use the delete
command to delete the latest toot our favourite and then try the
archive command again.

If you're not sure, you probably want to export the toots from your
archive, rename the file and restart from scratch. The archive you
need to delete is this file:
social.nasqueron.org.user.kensanata.json
```

So that's what you need to use:

```
$ mastodon-archive archive --append-all kensanata@social.nasqueron.org
Loading existing archive
Get user info
Get statuses (this may take a while)
Get favourites (this may take a while)
Saving 1 statuses and 1 favourites
```

# Troubleshooting

🔥 If you are archiving a ton of toots and you run into a General API
problem, use the `--pace` option. This is what the problem looks like:

```
$ mastodon-archive archive kensanata@dice.camp
...
Get statuses (this may take a while)
Traceback (most recent call last):
...
mastodon.Mastodon.MastodonAPIError: General API problem.
```

Solution:

```
$ mastodon-archive archive --pace kensanata@dice.camp
```

The problem seems to be related to how Mastodon [rate
limits](https://mastodonpy.readthedocs.io/en/latest/#a-note-about-rate-limits)
requests.

🔥 If you are expiring many toots, same thing. The default rate limit
is 300 requests per five minutes, so when more than 300 toots are to
be deleted, the app simply has to wait for five minutes before
continuing. It takes time.

```
$ mastodon-archive expire --confirm kensanata@octodon.social
Loading existing archive
Expiring |                                | 1/1236
We need to authorize the app to make changes to your account.
Log in
Visit the following URL and authorize the app:
[long URL here]
Then paste the access token here:
[access token here]
Default rate limiting is 300 requests per five minutes.
This will take a while.
Expiring |#######                         | 301/1236
```

🔥 If you are experimenting with a expiry, you'll need to give the app
write permissions. If you then delete the user secret file, hoping to
start with a clean slate when archiving, you'll be asked to authorize
the app again, but somehow Mastodon remembers that you have already
granted the app read and write permissions, and you will get this
error:

`mastodon.Mastodon.MastodonAPIError: Granted scopes "read write" differ from requested scopes "read".`

In order to get rid of this, you need to visit the website, got to
Settings → Authorized apps and revoke your authorization for
mastodon-archive. Now you can try the authorization URL again and you
will only get read permissions instead of both read and write
permissions.

# Documentation

The data we have in our archive file is a hash with three keys:

1. `account` is a [User dict](https://mastodonpy.readthedocs.io/en/latest/#user-dicts)
2. `statuses` is a list of [Toot dicts](https://mastodonpy.readthedocs.io/en/latest/#toot-dicts)
3. `favourites` is a list of [Toot dicts](https://mastodonpy.readthedocs.io/en/latest/#toot-dicts)

If you want to understand the details and the nested nature of these
data structures, you need to look at the Mastodon API documentation.
One way to get started is to look at what a
[Status](https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#status)
entity looks like.

# Development

If you checked out the repository and you want to run the code from
the working directory on a single user system, use `pip3 install
--upgrade --editable .` in your working directory to make it
"editable" (i.e. the system installation is linked to your working
directory, now).

If you don't want to do this for the entire system, you need your own
virtual environemt: `pip3 install virtualenvwrapper`, `mkvirtualenv ma
--python python3` (this installs and activates a virtual environment
called `ma`), `pip install -e .` (`-e` installs an "editable" copy)
and you're set. Use `workon ma` to work in that virtual environment in
the future.

# Processing using jq

[jq](https://stedolan.github.io/jq/) is a lightweight and flexible
command-line JSON processor. That means you can use it to work with
your archive.

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

# Exploring the API

Now that you have token files, you can explore the Mastodon API using
`curl`. Your *access token* is the long string in the file
`*.user.*.secret`. Here is how to use it.

Get a single status:

```
curl --silent --show-error \
     --header "Authorization: Bearer "$(cat dice.camp.user.kensanata.secret) \
     https://dice.camp/api/v1/statuses/99005111284322450
```

Extract the account id from your archive using `jq` and use `echo` to
[strip the surrounding double quotes](https://stackoverflow.com/a/24358387/534893).
Then use the id to get some statuses from the account and use `jq` to
print the status ids:

```
ID=$(eval echo $(jq .account.id < dice.camp.user.kensanata.json))
curl --silent --show-error \
     --header "Authorization: Bearer "$(cat dice.camp.user.kensanata.secret) \
     "https://dice.camp/api/v1/accounts/$ID/statuses?limit=3" \
     | jq '.[]|.id'
```

# Alternatives

There are two kinds of alternatives:

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
