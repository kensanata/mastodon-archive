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

from mastodon import Mastodon
import sys
import os.path
import json
import datetime


def archive(args):
    """
    Archive your toots and favourites from your Mastodon account
    """

    skip_favourites = args.skip_favourites
    
    (username, domain) = args.user.split("@")

    url = 'https://' + domain
    client_secret = domain + '.client.secret'
    user_secret = domain + '.user.' + username + '.secret'
    status_file = domain + '.user.' + username + '.json'
    data = None

    if os.path.isfile(status_file):
        print("Loading existing archive")
        with open(status_file, mode = 'r', encoding = 'utf-8') as fp:
            data = json.load(fp)

    if not os.path.isfile(client_secret):

        print("Registering app")
        Mastodon.create_app(
            'mastodon-archive',
            api_base_url = url,
            to_file = client_secret)

    if not os.path.isfile(user_secret):

        print("Log in")
        mastodon = Mastodon(
            client_id = client_secret,
            api_base_url = url)

        url = mastodon.auth_request_url(
            client_id = client_secret,
            scopes=['read'])

        print("Visit the following URL and authorize the app:")
        print(url)

        print("Then paste the access token here:")
        token = sys.stdin.readline().rstrip()

        mastodon.log_in(
            username = username,
            code = token,
            to_file = user_secret,
            scopes=['read'])

    else:

        mastodon = Mastodon(
            client_id = client_secret,
            access_token = user_secret,
            api_base_url = url)

    print("Get user info")
    user = mastodon.account_verify_credentials()

    def find_id(list, id):
        """Return the list item whose id attribute matches."""
        return next((item for item in list if item["id"] == id), None)

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
        page = page[0:page.index(found)]
        statuses.extend(page)
        print("Fetched a total of %d new toots" % len(statuses))
        return statuses

    if data is None or not "statuses" in data:
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
    elif data is None or not "favourites" in data:
        print("Get favourites (this may take a while)")
        favourites = mastodon.favourites()
        favourites = mastodon.fetch_remaining(
            first_page = favourites)
    else:
        id = data["favourites"][0]["id"]
        print("Get new favourites")
        favourites = fetch_up_to(mastodon.favourites(), id)
        favourites.extend(data["favourites"])

    data = { 'account': user,
            'statuses': statuses,
            'favourites': favourites }

    print("Saving %d statuses and %d favourites" % (
        len(statuses),
        len(favourites)))

    date_handler = lambda obj: (
        obj.isoformat()
        if isinstance(obj, (datetime.datetime, datetime.date))
        else None)

    with open(status_file, mode = 'w', encoding = 'utf-8') as fp:
        data = json.dump(data, fp, indent = 2, default = date_handler)

