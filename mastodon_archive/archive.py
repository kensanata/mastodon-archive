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
from . import core

def archive(args):
    """
    Archive your toots and favourites from your Mastodon account
    """

    append = args.append
    skip_favourites = args.skip_favourites
    with_mentions = args.with_mentions

    (username, domain) = args.user.split("@")

    status_file = domain + '.user.' + username + '.json'
    data = core.load(status_file)

    if append and data is None:
        print("Error: --append-all cannot be used with an empty data file",
              file=sys.stderr)
        sys.exit(3)

    mastodon = core.login(args)

    print("Get user info")

    try:
        user = mastodon.account_verify_credentials()
    except Exception as e:
        print(e, file=sys.stderr)
        if "access token was revoked" in str(e):
            core.deauthorize(args)
            archive(args)
            sys.exit(0)

    def find_id(list, id):
        """Return the list item whose id attribute matches."""
        for item in list:
            if str(item["id"]) == str(id) or "status" in item and str(item.status["id"]) == str(id):
                return item
        else:
            return None

    def fetch_up_to(page, id):
        statuses = []
        # use a generator expression to find our last status
        found = find_id(page, id)
        # get the remaining pages
        while len(page) > 0 and found is None:
            statuses.extend(page)
            sys.stdout.flush()
            page = mastodon.fetch_next(page)
            if page is None:
                break
            found = find_id(page, id)
        if found is None:
            print('''Error: I did not find the last toot we have in our archive.
Perhaps it was deleted?

If you have expired all the toots on your server, then this is
expected. In this case you need to use the --append-all option to make
sure we download all the toots on the server and append them to the
archive.

If you have never expired any toots and you just manually deleted or
unfavoured a toot online which happens to be the last one in the
archive, you could try to edit the archive file and delete the latest
toot or latest favourite and try the archive command again.

If you're not sure, you probably want to export the toots from your
archive, rename the file and restart from scratch. The archive you
need to delete is this file:
%s''' % status_file,
                  file=sys.stderr)
            sys.exit(4)
        else:
            page = page[0:page.index(found)]
            statuses.extend(page)
        print("Fetched a total of %d new toots" % len(statuses))
        return statuses

    def keep_mentions(notifications):
        return [x.status for x in notifications if x.type == "mention"]
    
    if append:
        print("Get statuses (this may take a while)")
        statuses = mastodon.account_statuses(user["id"])
        statuses = mastodon.fetch_remaining(
            first_page = statuses)
        statuses.extend(data["statuses"])
    elif data is None or not "statuses" in data or len(data["statuses"]) == 0:
        print("Get statuses (this may take a while)")
        statuses = mastodon.account_statuses(user["id"])
        statuses = mastodon.fetch_remaining(
            first_page = statuses)
    else:
        id = data["statuses"][0]["id"]
        print("Get new statuses")
        statuses = fetch_up_to(mastodon.account_statuses(user["id"]), id)
        statuses.extend(data["statuses"])

    if skip_favourites:
        print("Skipping favourites")
        if data is None or not "favourites" in data:
            favourites = []
        else:
            favourites = data["favourites"]
    elif append:
        print("Get favourites (this may take a while)")
        favourites = mastodon.favourites()
        favourites = mastodon.fetch_remaining(
            first_page = favourites)
        favourites.extend(data["favourites"])
    elif data is None or not "favourites" in data or len(data["favourites"]) == 0:
        print("Get favourites (this may take a while)")
        favourites = mastodon.favourites()
        favourites = mastodon.fetch_remaining(
            first_page = favourites)
    else:
        id = data["favourites"][0]["id"]
        print("Get new favourites")
        favourites = fetch_up_to(mastodon.favourites(), id)
        favourites.extend(data["favourites"])

    if not with_mentions:
        print("Skipping mentions")
        if data is None or not "mentions" in data:
            mentions = []
        else:
            mentions = data["mentions"]
    elif append:
        print("Get mentions (this may take a while)")
        notifications = mastodon.notifications()
        notifications = mastodon.fetch_remaining(
            first_page = notifications)
        mentions = keep_mentions(notifications)
        mentions.extend(data["mentions"])
    elif data is None or not "mentions" in data or len(data["mentions"]) == 0:
        print("Get mentions (this may take a while)")
        notifications = mastodon.notifications()
        notifications = mastodon.fetch_remaining(
            first_page = notifications)
        mentions = keep_mentions(notifications)
    else:
        id = data["mentions"][0]["id"]
        print("Get new notifications")
        notifications = fetch_up_to(mastodon.notifications(), id)
        mentions = keep_mentions(notifications)
        mentions.extend(data["mentions"])

    data = {
        'account': user,
        'statuses': statuses,
        'favourites': favourites,
        'mentions': mentions
    }

    print("Saving %d statuses, %d favourites, and %d mentions" % (
        len(statuses),
        len(favourites),
        len(mentions)))

    core.save(status_file, data)
