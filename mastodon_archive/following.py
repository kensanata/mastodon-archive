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

def is_lurker(account, mentions):
    for mention in mentions:
        if account["id"] == mention["account"]["id"]:
            return False
    return True

def find_lurkers(followers, whitelist, mentions):
    return [x for x in followers
            if x["acct"] not in whitelist
            and is_lurker(x, mentions)]

def following(args):
    """
    List people you're following but who never mention you
    """

    (username, domain) = args.user.split('@')

    status_file = domain + '.user.' + username + '.json'
    data = core.load(status_file, required=True, quiet=True, combine=True)

    # Print both error messages if the data is missing
    error = 0
    if "mentions" not in data or len(data["mentions"]) == 0:
        print("You need to run 'mastodon-archive archive --with-mentions'",
              file=sys.stderr)
        error = 5
    if "following" not in data or len(data["following"]) == 0:
        print("You need to run 'mastodon-archive archive --with-following'",
              file=sys.stderr)
        error = 6
    if error > 0:
        sys.exit(error)

    if args.all:
        print("Considering the entire archive")
        mentions = data["mentions"]
    else:
        print("Considering the last "
              + str(args.weeks)
              + " weeks")
        mentions = core.keep(data["mentions"], args.weeks)

    whitelist = core.whitelist(domain, username)

    if args.unfollow:
        mastodon = core.readwrite(args)
        accounts = find_lurkers(data["following"], whitelist, data["mentions"])

        bar = Bar('Unfollowing', max = len(accounts))

        for account in accounts:
            bar.next()
            try:
                mastodon.account_unfollow(account["id"])
            except Exception as e:
                if "authorized scopes" in str(e):
                    print("\nWe need to authorize the app to make changes to your account.")
                    core.deauthorize(args)
                    mastodon = core.readwritefollow(args)
                    # retry
                    mastodon.account_block(account["id"])
                else:
                    print(e, file=sys.stderr)

        bar.finish()

    else:
        accounts = find_lurkers(data["following"], whitelist, data["mentions"])
        for account in sorted(accounts, key=lambda account:
                              account["display_name"] or account["username"]):
            print("%s <%s>" % (account["display_name"] or account["username"],
                               account["acct"]))
