# Mastodon Backup

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Mastodon Backup](#mastodon-backup)
    - [Making a backup](#making-a-backup)
    - [Generating a text file](#generating-a-text-file)

<!-- markdown-toc end -->

## Making a backup

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

## Generating a text file

The tool `mastodon-backup-to-text.py` requires `html2text`:

```bash
# Python 3
pip3 install html2text
```

Assuming you already made a backup of your toots:

```
$ ./mastodon-backup-to-text.py kensanata@dice.camp
```
