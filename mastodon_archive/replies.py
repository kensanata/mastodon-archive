#!/usr/bin/env python3
# Copyright (C) 2019  Alex Schroeder <alex@gnu.org>

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
from progress.bar import Bar
from . import core

def replies(args):
    """
    Archive the statuses you replied to
    """

    (username, domain) = core.parse(args.user)

    status_file = domain + '.user.' + username + '.json'
    data = core.load(status_file, required = True)

    mastodon = core.login(args)

    print("Get user info")

    try:
        user = mastodon.account_verify_credentials()
    except Exception as e:
        if "access token was revoked" in str(e):
            core.deauthorize(args)
             # retry and exit without an error
            archive(args)
            sys.exit(0)
        elif "Name or service not known" in str(e):
            print("Error: the instance name is either misspelled or offline",
              file=sys.stderr)
        else:
            print(e, file=sys.stderr)
        # exit in either case
        sys.exit(1)

    index = {} # mapping ids to statuses
    missing = [] # ids we need to fetch

    for collection in ["statuses",
                       "favourites",
                       "mentions",
                       "replies"]:
        if collection not in data:
            print("No %s in this archive..." % collection)
        else:
            statuses = data[collection];
            print("Indexing %d %s..." % (len(statuses), collection))
            for status in statuses:

                if status["reblog"] is not None:
                    status = status["reblog"]

                # only accept one status per id
                if status["id"] in index:
                    pass
                else:
                    index[status["id"]] = 1
    print("Indexed %d statuses..." % (len(index)))

    print("Counting missing replies...")
    for status in data["statuses"]:
        # skip boosts
        if status["reblog"] is None and status["in_reply_to_id"] is not None:
            if status["in_reply_to_id"] not in index:
                missing.append(status["in_reply_to_id"])
    print("Missing %d originals..." % (len(missing)))

    if len(missing) > 300:
        print("Given the typical rate limit of 300 requests per 5 minutes, "
              "this will take about %d minutes" % (len(missing) // 300 * 5))

    if len(missing) > 0:
        if not "replies" in data:
            replies = []
        else:
            replies = data["replies"]

        bar = Bar('Fetching', max = len(missing))

        for id in missing:
            try:
                status = mastodon.status(id)
                replies.append(status)
            except Exception as e:
                if  "not found" in str(e):
                    pass
                else:
                    print(e, file=sys.stderr)

            bar.next()

        bar.finish()

        data["replies"] = replies
        core.save(status_file, data)
