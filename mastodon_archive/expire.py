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
from . import core

def delete(mastodon, collection, status):
    """
    Delete toot or unfavour favourite and mark it as deleted.
    The "record not found" error is handled elsewhere.
    """
    if collection == 'statuses':
        mastodon.status_delete(status["id"]);
    elif collection == 'favourites':
        mastodon.status_unfavourite(status["id"])
    status["deleted"] = True

def expire(args):
    """
    Expire toots: delete toots and unfavour favourites older than a few weeks
    """

    confirmed = args.confirmed
    collection = args.collection

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
        return created < cutoff and not deleted

    statuses = list(filter(matches, data[collection]))
    n_statuses = len(statuses)

    if (n_statuses == 0):
        print("No statuses are older than %d weeks" % args.weeks,
              file=sys.stderr)
        sys.exit(3)
    elif (True or n_statuses > 300):
        estimated_time = math.floor((n_statuses - 1) / 300) * 5
        print("Considering the default rate limit of 300 requests per five minutes and having {} statuses,\n"
              "this will take at least {} minutes to complete.".format(n_statuses, estimated_time))

    if confirmed:

        bar = Bar('Expiring', max = len(statuses))

        for status in statuses:
            bar.next()
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
                else:
                    print(e, file=sys.stderr)

        bar.finish()

        core.save(status_file, data)

    else:

        for status in statuses:
            if collection == 'statuses':
                print ("Delete: %s \"%s\"" % (
                    status["created_at"][0:10],
                    status["content"][0:60] +
                    ('...' if len(status["content"]) > 60 else '')))
            elif collection == 'favourites':
                print ("Unfavour: %s \"%s\"" % (
                    status["created_at"][0:10],
                    status["content"][0:60] +
                    ('...' if len(status["content"]) > 60 else '')))
