# Mastodon Archive

This tool allows you to make an archive of your statuses, your
favourites and the media in both your statuses and your favourites.
From this archive, you can generate a simple text file, or a HTML file
with or without media. Take a look at an
[example](https://alexschroeder.ch/mastodon.weaponvsac.space.user.kensanata.html)
if you're curious.

Note that Mastodon
[v2.3.0](https://github.com/tootsuite/mastodon/releases/tag/v2.3.0)
added an account archive download feature: "Every 7 days you are able
to request a full archive of your toots. The toots are exported in
ActivityPub JSON format alongside the media files attached to them,
your avatar and header images as well as the private key of your
account used for signing content." If all you want to do is have a
backup of your data, perhaps that is enough and you don't need this
tool.

Please report issues on the
[Software Wiki](https://alexschroeder.ch/software/Mastodon_Archive).
You can get the latest sources
[from the author’s site](https://alexschroeder.ch/cgit/mastodon-archive/about/).

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Installation](#installation)
- [Making an archive](#making-an-archive)
- [Splitting an archive](#splitting-an-archive)
- [Downloading media files](#downloading-media-files)
- [Generating a text file](#generating-a-text-file)
- [Searching your archive](#searching-your-archive)
- [Show context for a toot](#show-context-for-a-toot)
- [Generating a HTML file](#generating-a-html-file)
- [Reporting](#reporting)
- [Expiring your toots and favourites](#expiring-your-toots-and-favourites)
- [Troubleshooting](#troubleshooting)
- [Followers](#followers)
- [Following](#following)
- [Whitelist](#whitelist)
- [Mutuals](#mutuals)
- [Example Setup](#example-setup)
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
pip3 install mastodon-archive
```

If this is the first tool you installed using `pip` then perhaps it
installed `mastodon-archive` in a directory that's not on your `PATH`.
I had to add the following to my `~/.bashrc` file:

```bash
export PATH=$PATH:$HOME/.local/bin
```

🔥 If you're getting an error that ends with `Command "python setup.py
egg_info" failed with error code 1 ...` you might have to install the
setup tools. Try the following:

```bash
pip3 install --user setuptools
pip3 install mastodon-archive
```

# Making an archive

When using the app for the first time, you have to authorize it:

```text
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

```text
$ mastodon-archive archive --no-favourites kensanata@dice.camp
```

If you want a better picture of conversations, you can also include
mentions. Mentions are notifications of statuses in which you were
mentioned as opposed to statuses of yours that were favoured or
boosted by others. Note that if you used to *dismiss* notifications
using the "Clear notifications" menu, then no mentions will be found
as mentions are simply a particular kind of notification.

```text
$ mastodon-archive archive --with-mentions kensanata@dice.camp
```

No matter what you did, You will end up with three new files:

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

# Splitting an archive

If you keep adding your archive, it eventually grows very large. When
it reaches hundreds of megabytes, consider *splitting* it.

```
$ ls -lh *.json
-rw-r--r-- 1 alex alex 120M Apr 14 21:50 octodon.social.user.kensanata.json
```

You can provide an `--older-than` option to specify the number of
weeks you want to keep. The default is four weeks.

If you don't provide the `--confirmed` option, this is a dry run.

```
$ mastodon-archive split --older-than=10 kensanata@octodon.social
This is a dry run and nothing will be moved.
Instead, we'll just list what would have happened.
Use --confirmed to actually do it.
Loading existing archive
Older than 2019-02-03 22:11:48.253408
statuses: 10623
favourites: 11233
mentions: 10773
Would have saved this to octodon.social.user.kensanata.0.json
```

When you do the split, the files are saved.

```
$ mastodon-archive split --older-than=10 --confirmed kensanata@octodon.social
Loading existing archive
Older than 2019-02-03 22:11:59.668432
statuses: 10623
favourites: 11233
mentions: 10773
Saving octodon.social.user.kensanata.json
Saving octodon.social.user.kensanata.0.json
```

Verify the result:

```
$ ls -lh *.json
-rw-r--r-- 1 alex alex 107M Apr 14 22:12 octodon.social.user.kensanata.0.json
-rw-r--r-- 1 alex alex  13M Apr 14 22:12 octodon.social.user.kensanata.json
```

# Downloading media files

Assuming you already made an archive of your toots:

```text
$ mastodon-archive media kensanata@dice.camp
44 urls in your archive (half of them are previews)
34 files already exist
Downloading |################################| 10/10
```
By default, media you uploaded and media of statuses you added your
favourites are not part of your archive. To download these too,
specify the favourites collection:

```text
$ mastodon-archive media --collection favourites kensanata@dice.camp
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

```text
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

```text
$ mastodon-archive text kensanata@dice.camp > statuses.txt
```

If you're working with text, you might expect the first toot to be at
the top and the last toot to be at the bottom. In this case, you need
to reverse the list:

```text
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

```text
$ mastodon-archive text kensanata@dice.camp house
```

You can provide multiple regular expressions and they will all be
checked:

```text
$ mastodon-archive text kensanata@dice.camp house rule
```

Remember basic
[regular expression syntax](https://docs.python.org/3/library/re.html#regular-expression-syntax):
`\b` is a word boundary, `(?i)` ignores case, `(a|b)` is for
alternatives, just to pick some useful ones. Use single quotes to
protect your backslashes and questionmarks.

```text
$ mastodon-archive text kensanata@dice.camp house 'rule\b'
```

You can also search your favourites or your mentions:

```text
$ mastodon-archive text --collection favourites kensanata@dice.camp '(?i)blackbird'
```

Dates are in ISO format (e.g. `2017-11-19T14:00`). I usually only care
about year and month, though:

```text
$ mastodon-archive text --collection favourites kensanata@dice.camp bird '2017-(07|08|09|10|11)'
```


# Show context for a toot

Sometimes you only remember something about a *thread*. Let's say you
asked a question a while back but now you can't remember the answer
you got back then. First, find the question:

```text
$ mastodon-archive text kensanata@dice.camp rules
Alex Schroeder 🐉 @kensanata 2018-05-28T21:19:27.483000+00:00
https://dice.camp/@kensanata/100109016572069901
...
```

Using the URL, you can now search the archive for some context:

```text
$ mastodon-archive context kensanata@dice.camp https://dice.camp/@kensanata/100109016572069901
```

This shows the same information clicking on the toot shows you in the
web client: all its ancestors and all its descendants. Obviously, if
these toots are not in your archive, we can't find them. You'll have
to click on the links and hope they're still around.


# Generating a HTML file

Assuming you already made an archive of your toots:

```text
$ mastodon-archive html kensanata@dice.camp
```

This will create numbered HTML files starting with
`dice.camp.user.kensanata.statuses.0.html`, each page with 2000 toots.

You can change the number of toots per page using an option:

```text
$ mastodon-archive html --toots-per-page 100 kensanata@dice.camp
```

If you have downloaded your media attachments, these will be used in
the HTML files. Thus, if you want to upload the HTML files, you now
need to upload the media directory as well or all the media links will
be broken.

You can also generate a file for your favourites:

```text
$ mastodon-archive html --collection favourites kensanata@dice.camp
```

This will create numbered HTML files starting with
`dice.camp.user.kensanata.favourites.0.html`, each page with 2000
toots.

Note that both the HTML file with your statuses and the HTML file with
your favourites will refer to the media files in your media directory.

# Reporting

Some numbers, including your ten most used hashtags:

```text
$ mastodon-archive report kensanata@dice.camp
Considering the last 12 weeks
Statuses:               296
Boosts:                  17
Media:                    9

Top 10 hashtags:
#caster(8) #20questions(5) #osr(3) #dungeonslayers(2) #introduction(2)
#currentprojects(2) #diaspora(1) #gygax(1) #yoonsuin(1) #casters(1)

Favourites:             248
Boosts:                   0
Media:                   20

Top 10 hashtags:
#1strpg(9) #rpg(5) #myfirstcharacter(5) #introduction(5) #osr(4)
#1strpgs(4) #dnd(3) #gamesnacks(1) #vancian(1) #mastoart(1)
```

You can specify a different time number of weeks to consider using
`--newer-than N` or use `--all` to consider all your statuses and
favourites.

You can list a different number of hashtags using `--top N` and you
can list all of them by using `--top -1`. This might result in a very
long list.

By default only your toots are considered for the hashtags. Use `--include-boosts` to also include toot you have boosted.

# Expiring your toots and favourites

**Warning**: This is a destructive operation. You will delete your
toots on your instance, or unfavour your favourites, or dismiss your
notifications on your instance. Where as it might be possible to
favour all your favourites again, there is no way to repost all those
toots. You will have a copy in your archive, but there is no way to
restore these to your instance.

**But why?** I might want to keep a copy of my toots, but I don't
think they have much value going back months and years. I never read
through years of tweeting history! This only benefits your enemies,
never your friends. So I want to expire my toots. We can always write
a blog post about the good stuff. You can read more about this [on my
blog](https://alexschroeder.ch/wiki/2017-04-27_Record_Keeping).

**Alternatives**: Check out [forget](https://forget.codl.fr/about/)
which is a web app that only expires your toots without archiving
them.
[MastoPurgee](https://github.com/ThomasLeister/mastopurge/blob/master/README.md)
does the same thing but it's a stand-alone binary. Depending on your
needs, these might be good enough.

Anyway, back to *Mastodon Archive*. 🙂

Sadly, I have some bad news for you: this has been rate limited to
[30 statuses per 30 minutes](https://mastodon.social/@Gargron/101588449409740014)!
😭

No, really! See the [merge request](https://github.com/tootsuite/mastodon/pull/10042).
This is terrible. Expiry basically only works if you run it every time
you have posted 30 statuses or so, in the long run. If you don't, be
prepared for a *long* wait! 😴

In order to not go crazy, the code catches an interrupt (such as you
pressing `Ctrl-C`) and saves the data even though it hasn't finished
expiring your statuses.

Anyway, enough complaining. How do you do it?

You can expire your toots using the `expire` command and providing the
`--older-than` option. This option specifies the number of weeks to
keep on the server. Anything older than that is deleted or unfavoured.
If you use `--older-than 0`, then *all* your toots will be deleted, or
*all* your favourites will be unfavoured, or *all* your notifications
will be dismissed.

```text
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

```text
$ mastodon-archive expire --collection favourites --older-than 0 \
  --confirmed kensanata@social.nasqueron.org
Log in
Visit the following URL and authorize the app:
[long URL shown here]
Then paste the access token here:
[long token pasted here]
Expiring |################################| 1/1
```

After a while you'll notice that archiving mentions takes more and
more time. The reason is when expiring mentions, the tool goes through
all your notifications and looks at those of the type "mention" and
expires them if they are old enough. There are other types of
notifications, however: "follow", "favourite", and "reblog" (at the
time of this writing). As these are not archived, we also don't expire
them. Thus, the list of notifications to look through when archiving
keeps growing unless you use the "Clear notifications" menu in the
Mastodon web client. Alternatively, you can use the
`--delete-other-notifications` option together with `--collection
mentions` and then the tool will dismiss all the older other
notifications for you.

# Troubleshooting

🔥 If you are archiving a ton of toots and you run into a General API
problem, use the `--pace` option. This is what the problem looks like:

```text
$ mastodon-archive archive kensanata@dice.camp
...
Get statuses (this may take a while)
Traceback (most recent call last):
...
mastodon.Mastodon.MastodonAPIError: General API problem.
```

Solution:

```text
$ mastodon-archive archive --pace kensanata@dice.camp
```

The problem seems to be related to how Mastodon [rate
limits](https://mastodonpy.readthedocs.io/en/latest/#a-note-about-rate-limits)
requests.

🔥 If you are expiring many toots, same thing. The default rate limit
is 300 requests per five minutes, so when more than 300 toots are to
be deleted, the app simply has to wait for five minutes before
continuing. It takes time.

```text
$ mastodon-archive expire --confirm kensanata@octodon.social
Loading existing archive
Expiring |                                | 1/1236
We need to authorize the app to make changes to your account.
Log in
Visit the following URL and authorize the app:
[long URL here]
Then paste the access token here:
[access token here]
Considering the default rate limit of 300 requests per five minutes and having 1236 statuses,
this will take at least 20 minutes to complete.
Expiring |#######                         | 301/1236
```

🔥 If you are experimenting with expiry, you'll need to give the app
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

# Followers

This is work in progress. I'm actually not sure where I want to go
with this. Right now it lists all your followers that haven't
interacted with you. If a toot of theirs mentions you, then that
counts as an interaction. Favouring and boosting does not count. By
default, this looks at the last twelve weeks. In order for this to
work, you need an archive containing both mentions and followers.

```text
$ mastodon-archive archive --with-mentions --with-followers kensanata@dice.camp
Loading existing archive
Get user info
Get new statuses
Fetched a total of 0 new toots
Get new favourites
Fetched a total of 0 new toots
Get new notifications
Fetched a total of 2 new toots
Get followers (this may take a while)
Saving 659 statuses, 376 favourites, 478 mentions, and 107 followers
```

Now you're ready to determine the list of lurkers:

```text
$ mastodon-archive followers kensanata@dice.camp
Considering the last 12 weeks
There is no whitelist
...
```

As I said, this is work in progress and I don't really know where I'm
going with this. More
[on my blog](https://alexschroeder.ch/wiki/2018-04-13_Social_Media_Goals).

This command supports the [whitelist](#whitelist).

# Following

Assume you're on the fediverse just for the conversation. You're not
actually interested in following anybody who never talks to you: no
journalists, no famous people, no pundits. You just want to follow
regular people who interact with you. You can list the people you're
following who never mentioned you, and you can unfollow them all!

There are two prerequisites, however:

1. you need to add the people you're following to the archive
2. you need to add the mentions to the archive (this can take a long time)

```text
$ mastodon-archive archive --with-following --with-mentions kensanata@dice.camp
Loading existing archive
Get user info
Get new statuses
X
Added a total of 11 new items
Get new favourites
X
Added a total of 7 new items
Get new notifications and look for mentions
.....
Added a total of 7 new items
Skipping followers
Get following (this may take a while)
Saving 932 statuses, 527 favourites, 657 mentions, 107 followers, and 192 following
```

Given this data, you can now list the people we're interested in:

```text
$ mastodon-archive following kensanata@dice.camp
Considering the last 12 weeks
...
```

All these people that never mentioned you: do you really want to
follow them all? If you don't, here's how to unfollow them:

```text
$ mastodon-archive following --unfollow kensanata@dice.camp
Considering the last 12 weeks
Unfollowing |################################| 1/125
We need to authorize the app to make changes to your account.
Registering app
This app needs access to your Mastodon account.
Visit the following URL and authorize the app:
[long URL here]
Then paste the access token here:
[access token here]
```

Note that the application needs the permission to unfollow people in
your name, which is why you need to authorize it again.

This command supports the [whitelist](#whitelist).

# Whitelist

You can have a whitelist of people you want to be exempt from some
commands. Create a text file with a name like the following:
`dice.camp.user.kensanata.whitelist.txt`.

That is: `<your domain>.user.<your account>.whitelist.txt`.

There, list the accounts you want to have in your whitelist, one per
line. All of these formats should work:

```text
kensanata
kensanata@dice.camp
Alex Schroeder <kensanata@dice.camp>
```

To verify your whitelist, use the whitelist command:

```text
$ mastodon-archive whitelist kensanata@dice.camp
2 accounts are on the whitelist
kensanata@dice.camp
kensanata
```

Using `wc -l` to count the lines in my output, here's how you can see
that it works:

```text
$ mastodon-archive followers kensanata@dice.camp | wc -l
58
$ echo linkskywalker@soc.ialis.me >> dice.camp.user.kensanata.whitelist.txt
$ mastodon-archive followers kensanata@dice.camp | wc -l
57
```

# Mutuals

How do you go about creating a whitelist, though? It's hard! You could
start with the list of people that are following you back, perhaps?
Here's a command to do just that:

```text
$ mastodon-archive mutuals kensanata@dice.camp
Get user info
...
```

We don't currently store the relationship status in our archive so
that's why this command requires a live connection. We do have the
list of people we are *following* in our archive, so we use that. If
you haven't done so, you need to create an archive using the
`--with-following` option before you can use the `mutuals` command.

```text
$ mastodon-archive archive --with-following kensanata@dice.camp
Loading existing archive
...
```

# Example Setup

I have a shell script called `backup-mastodon` which does the following:

```sh
#!/bin/sh
mkdir -p ~/Documents/Mastodon/
cd ~/Documents/Mastodon/ || exit

accounts="kensanata@octodon.social kensanata@dice.camp kensanata@tabletop.social"

echo Archive Statuses, Favourites, Mentions
for acc in $accounts; do
    echo "$acc"
    mastodon-archive archive --with-mentions "$acc"
done

echo Expiring Statuses
for acc in $accounts; do
    echo "$acc"
    mastodon-archive expire --older-than 8 --collection statuses --confirm "$acc"
done

echo Expiring Favourites
for acc in $accounts; do
    echo "$acc"
    mastodon-archive expire --older-than 8 --collection favourites --confirm "$acc"
done

echo Dismissing Notifications
for acc in $accounts; do
    echo "$acc"
    mastodon-archive expire --older-than 8 --collection mentions --delete-other-notifications --confirm "$acc"
done
```

# Documentation

The data we have in our archive file is a hash with three keys:

1. `account` is a [User dict](https://mastodonpy.readthedocs.io/en/latest/#user-dicts)
2. `statuses` is a list of [Toot dicts](https://mastodonpy.readthedocs.io/en/latest/#toot-dicts)
3. `favourites` is a list of [Toot dicts](https://mastodonpy.readthedocs.io/en/latest/#toot-dicts)
4. `mentions` is a list of [Toot dicts](https://mastodonpy.readthedocs.io/en/latest/#toot-dicts)

If you want to understand the details and the nested nature of these
data structures, you need to look at the Mastodon API documentation.
One way to get started is to look at what a
[Status](https://github.com/tootsuite/documentation/blob/master/Using-the-API/API.md#status)
entity looks like.

# Development

The
[setup.py](https://setuptools.readthedocs.io/en/latest/setuptools.html#automatic-script-creation)
determines how the app is installed and what its dependencies are.

If you checked out the repository and you want to run the code from
the working directory on a single user system, use `sudo pip3 install
--upgrade --editable .` in your working directory to make it is
"editable" (i.e. the installation you have is linked to your working
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

```sh
$ jq '[.favourites[] | {time: .account.username, message: .content}]' < dice.camp.user.kensanata.json
```

Example output, assuming I had only a single favourite:

```json
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

```sh
curl --silent --show-error \
     --header "Authorization: Bearer "$(cat dice.camp.user.kensanata.secret) \
     https://dice.camp/api/v1/statuses/99005111284322450
```

Extract the account id from your archive using `jq` and use `echo` to
[strip the surrounding double quotes](https://stackoverflow.com/a/24358387/534893).
Then use the id to get some statuses from the account and use `jq` to
print the status ids:

```sh
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
