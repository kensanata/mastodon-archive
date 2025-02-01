#!/usr/bin/env python3
# Copyright (C) 2017  Alex Schroeder <alex@gnu.org>
# Copyright (C) 2017  Steve Ivy <steveivy@gmail.com>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

import sys
import os.path
import math
from progress.bar import Bar
from datetime import timedelta, datetime
from random import shuffle
import signal
import html2text
import textwrap
from . import core

h = html2text.HTML2Text()
h.ignore_links = True

def text(status):
    text = textwrap.fill(h.handle(status["content"])).lstrip();
    text = text.replace("\n", " ")
    if len(text) > 50:
        text = text[0:50] + '...'
    return "%s \"%s\"" % (status["created_at"][0:10], text)

def delete(mastodon, collection, status):
    """
    Delete toot or unfavour favourite and mark it as deleted. The
    "record not found" error is handled elsewhere. Mentions cannot be
    dismissed because mastodon.notifications_dismiss requires a
    notification id, not a status id.
    """
    if collection == 'statuses':
        if status["reblog"]:
            mastodon.status_unreblog(status["reblog"]["id"])
            status["deleted"] = True
        else:
            mastodon.status_delete(status["id"])
            status["deleted"] = True
    elif collection == 'favourites':
        mastodon.status_unfavourite(status["id"])
        status["deleted"] = True

def expire(args):
    """
    Expire toots: delete toots, unfavour favourites, or dismiss
    notifications older than a few weeks
    """

    confirmed = args.confirmed
    collection = args.collection
    delete_others = args.delete_others

    if (delete_others and collection != 'mentions'):
        print("The --delete-others option can only be used "
              "together with --collection mentions.",
              file=sys.stderr)
        sys.exit(4)

    (username, domain) = args.user.split('@')

    status_file = domain + '.user.' + username + '.json'
    data = core.load(status_file, required = True, quiet = True)

    if confirmed:
        mastodon = core.readwrite(args)
    else:
        print("This is a dry run and nothing will be expired.\n"
              "Instead, we'll just list what would have happened.\n"
              "Use --confirmed to actually do it.")

    delta = timedelta(weeks = args.weeks)
    cutoff = datetime.today() - delta

    def matches(status):
        created = datetime.strptime(status["created_at"][0:10], "%Y-%m-%d")
        deleted = "deleted" in status and status["deleted"] == True
        pinned = "pinned" in status and status["pinned"] == True
        return created < cutoff and not deleted and not pinned

    if collection != "mentions":

        statuses = list(filter(matches, data[collection]))
        n_statuses = len(statuses)
        shuffle(statuses)

        if (n_statuses == 0):
            print(f"No {collection} are older than {args.weeks} weeks",
                  file=sys.stderr)

        if confirmed and n_statuses > 0:

            bar = Bar('Expiring', max = len(statuses))
            error = ''

            def signal_handler(signal, frame):
                print("\nYou pressed Ctrl+C! Saving data before exiting!")
                core.save(status_file, data)
                sys.exit(0)

            signal.signal(signal.SIGINT, signal_handler)

            i = 1
            for status in statuses:
                try:
                    delete(mastodon, collection, status)
                    if i % 300 == 0:
                        core.save(status_file, data, quiet=True, backup=False)
                    i = i+1
                    bar.next()
                except Exception as e:
                    if "authorized scopes" in str(e):
                        print("\nWe need to authorize the app to make changes to your account.")
                        core.deauthorize(args)
                        mastodon = core.readwrite(args)
                        # retry
                        delete(mastodon, collection, status)
                    elif "not found" in str(e):
                        status["deleted"] = True
                        bar.next()
                    elif "Name or service not known" in str(e):
                        error = "Error: the instance name is either misspelled or offline"
                    else:
                        print(e, file=sys.stderr)

            bar.finish()

            if error:
                print(error, file=sys.stderr)

            core.save(status_file, data, quiet=args.quiet)

        elif n_statuses > 0:

            for status in statuses:
                if collection == 'statuses':
                    if not args.quiet:
                        print("Delete: " + text(status))
                elif collection == 'favourites':
                    if not args.quiet:
                        print("Unfavour: " + text(status))

    if collection == "mentions":

        if delete_others:
            if not args.quiet:
                print('Dismissing mentions and other notifications')
        else:
            if not args.quiet:
                print('Dismissing mentions')

        if not args.quiet:
            progress = core.progress_bar()

        # only consider statuses with an id (no idea what the others are)
        statuses = list(filter(lambda x: "id" in x, data[collection]))
        if not args.quiet:
            n_statuses = len(statuses)
            print("Mentions already archived: " + str(n_statuses))

        # create a dictionary for fast lookup of archived statuses that mention us
        ids = { x["id"]: True for x in statuses }

        # The date format here is slightly different. We expire
        # notifications if we have the status is a mention in our
        # archive, or if the status is not a mention and
        # --delete-others was used -- and if if it is older than the
        # cutoff period, of course.
        def matches(notifications):
            return [x for x in notifications
                    if (x.id in ids if x.type == "mention" else delete_others)
                    and x["created_at"].replace(tzinfo = None) < cutoff]

        mastodon = core.login(args)
        notifications = mastodon.notifications(limit=100)
        error = ''
        total = 0
        dismissed = 0
        while (notifications):
            if not args.quiet:
                progress()
            total += len(notifications)
            for notification in matches(notifications):
                if confirmed:
                    try:
                        mastodon.notifications_dismiss(notification["id"])
                        dismissed += 1
                    except Exception as e:
                        if "authorized scopes" in str(e):
                            print("\nWe need to authorize the app to make changes to your account.")
                            core.deauthorize(args)
                            mastodon = core.readwrite(args)
                            # retry
                            mastodon.notifications_dismiss(notification["id"])
                            dismissed += 1
                        elif "not found" in str(e):
                            pass
                        elif "Name or service not known" in str(e):
                            error = "Error: the instance name is either misspelled or offline"
                        else:
                            print(e, file=sys.stderr)
                else:
                    print("Dismiss"
                          # + str(notification["id"])
                          + " " + notification["created_at"].strftime("%Y-%m-%d")
                          + " " + notification["account"]["acct"]
                          + " " + notification["type"])

            notifications = mastodon.fetch_next(notifications)

        if error:
            print(error, file=sys.stderr)

        if not args.quiet:
            print(f"Dismissed {dismissed} of {total} notifications")
