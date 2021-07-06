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
    Delete toot, unfavour favourite, or dismiss notification and mark
    it as deleted. The "record not found" error is handled elsewhere.
    """
    if collection == 'statuses':
        if status["reblog"]:
            mastodon.status_unreblog(status["reblog"]["id"])
        else:
            mastodon.status_delete(status["id"])
    elif collection == 'favourites':
        mastodon.status_unfavourite(status["id"])
    elif collection == 'mentions':
        mastodon.notifications_dismiss(status["id"])
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
    data = core.load(status_file, required = True)

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

    statuses = list(filter(matches, data[collection]))
    n_statuses = len(statuses)
    shuffle(statuses)

    if (n_statuses == 0):
        print("No " + collection + " are older than %d weeks" % args.weeks,
              file=sys.stderr)

    if confirmed and n_statuses > 0:

        bar = Bar('Expiring', max = len(statuses))
        error = ''

        def signal_handler(signal, frame):
            print("\nYou pressed Ctrl+C! Saving data before exiting!")
            core.save(status_file, data)
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        for status in statuses:
            try:
                delete(mastodon, collection, status)
            except Exception as e:
                if "authorized scopes" in str(e):
                    print("\nWe need to authorize the app to make changes to your account.")
                    core.deauthorize(args)
                    mastodon = core.readwrite(args)
                    # retry
                    delete(mastodon, collection, status)
                elif "not found" in str(e):
                    status["deleted"] = True
                elif "Name or service not known" in str(e):
                    error = "Error: the instance name is either misspelled or offline"
                else:
                    print(e, file=sys.stderr)
            bar.next()

        bar.finish()

        if error:
            print(error, file=sys.stderr)

        core.save(status_file, data)

    elif n_statuses > 0:

        for status in statuses:
            if collection == 'statuses':
                print("Delete: " + text(status))
            elif collection == 'favourites':
                print("Unfavour: " + text(status))
            elif collection == 'mentions':
                print("Dismiss: " + text(status))

    if delete_others:
        print('Getting other notifications')

        # unlike above where we're getting the created_at value from
        # the JSON file where the date comes in iso format... see
        # core.save
        def others(notifications):
            return [x for x in notifications
                    if x.type != "mention"
                    and x["created_at"].replace(tzinfo = None) < cutoff]

        mastodon = core.login(args)
        notifications = mastodon.notifications(limit=100)
        notifications = mastodon.fetch_remaining(
            first_page = notifications)
        notifications = others(notifications)

        n_notifications = len(notifications)

        if (n_notifications == 0):
            print("No other notifications are older than %d weeks" % args.weeks,
                  file=sys.stderr)
        elif (n_notifications > 300):
            estimated_time = math.floor((n_notifications - 1) / 300) * 5
            print("Considering the default rate limit of 300 requests per five minutes\n"
                  "and having {} items, this will take at least {} minutes to complete.".format(n_notifications, estimated_time))

        if confirmed and n_notifications > 0:

            bar = Bar('Dismissing', max = n_notifications)
            error = ''

            for notification in notifications:
                bar.next()
                try:
                    mastodon.notifications_dismiss(notification["id"])
                except Exception as e:
                    if "authorized scopes" in str(e):
                        print("\nWe need to authorize the app to make changes to your account.")
                        core.deauthorize(args)
                        mastodon = core.readwrite(args)
                        # retry
                        mastodon.notifications_dismiss(notification["id"])
                    elif "not found" in str(e):
                        pass
                    elif "Name or service not known" in str(e):
                        error = "Error: the instance name is either misspelled or offline"
                    else:
                        print(e, file=sys.stderr)

            bar.finish()

            if error:
                print(error, file=sys.stderr)

        elif n_notifications > 0:

            for notification in notifications:
                print("Dismiss: "
                      + notification["created_at"].strftime("%Y-%m-%d")
                      + " " + notification["account"]["acct"]
                      + " " + notification["type"])
