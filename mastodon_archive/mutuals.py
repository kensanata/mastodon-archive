#!/usr/bin/env python3
# Copyright (C) 2018  Alex Schroeder <alex@gnu.org>

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
from datetime import timedelta, datetime
from . import core

def mutuals(args):
    """
    List people you're following and who are following you, too.
    """

    (username, domain) = args.user.split('@')

    status_file = domain + '.user.' + username + '.json'
    data = core.load(status_file, required=True, quiet=True, combine=True)

    # Print both error messages if the data is missing
    if "following" not in data or len(data["following"]) == 0:
        print("You need to run 'mastodon-archive archive --with-following'",
              file=sys.stderr)
        sys.exit(7)

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

    ids = [x["id"] for x in data["following"]]
    lookup = {x["id"]: "%s <%s>" % (x["display_name"] or x["username"],
                                      x["acct"])
              for x in data["following"]}
    relations = mastodon.account_relationships(ids)
    for relation in relations:
        if relation["followed_by"]:
            print(lookup[relation["id"]])
