#!/usr/bin/env python3
# Copyright (C) 2017-2018  Alex Schroeder <alex@gnu.org>

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
import datetime
import json
import glob
import re
import shutil

def parse(account):
    """
    Parse account into username and domain.
    """
    try:
        (username, domain) = account.split('@')
        return username, domain;
    except ValueError:
        print("The account has to have the form username@domain", file=sys.stderr)
        sys.exit(3)

def read(args):
    """
    Login to your Mastodon account with read-only permissions.
    """
    return login(args)

def readwrite(args):
    """
    Login to your Mastodon account with read and write permissions.
    Note that you will get an error when your authorization token is a
    read-only token. If this happens, you need to deauthorize and try
    again.
    """
    try:
        # this is what we expect
        return login(args, scopes = ['read', 'write'])
    except Exception as e:
        # on some instances, there's this problem with getting a
        # bigger scope than requested, so just do it again and hope
        # for the best... (dealing with MastodonAPIError: Granted
        # scopes "follow read write" differ from requested scopes
        # "read write".)
        return login(args, scopes = ['follow', 'read', 'write'])

def readwritefollow(args):
    """
    Login to your Mastodon account with read, write and follow permissions.
    Note that you will get an error when your authorization token is a
    read-only token. If this happens, you need to deauthorize and try
    again.
    """
    return login(args, scopes = ['follow', 'read', 'write'])

def deauthorize(args):
    """
    Deauthorize the account.
    """
    app = App(args.user)
    app.deauthorize()

def login(args, scopes=('read',)):
    """
    Login to your Mastodon account
    """
    pace = hasattr(args, 'pace') and args.pace
    app = App(args.user, scopes)
    return app.login(pace)


class App:
    """
    Client application to register, authorize and login with your Mastodon
    account.
    """

    def __init__(self, user, scopes=('read',), name="mastodon-archive"):

        self.username, self.domain = user.split("@")
        self.url = "https://" + self.domain
        self.name = name
        self.scopes = scopes
        self.client_secret = self.domain + ".client.secret"
        self.user_secret = self.domain + ".user." + self.username + ".secret"

    def register(self):
        """
        Register application and saves client secret.
        """
        print("Registering app")
        Mastodon.create_app(
            self.name,
            api_base_url=self.url,
            scopes=self.scopes,
            to_file=self.client_secret
        )

    def authorize(self):
        """
        Tries to authorize via OAuth API, and save access token. If it fails
        fallsback to username and password.
        """
        url = self.url
        client_secret = self.client_secret
        user_secret = self.user_secret
        scopes = self.scopes
        print("This app needs access to your Mastodon account.")

        mastodon = Mastodon(client_id=client_secret, api_base_url=url)

        url = mastodon.auth_request_url(client_id=client_secret, scopes=scopes)

        print("Visit the following URL and authorize the app:")
        print(url)

        print("Then paste the access token here:")
        token = sys.stdin.readline().rstrip()

        try:
            # on the very first login, --pace has no effect
            mastodon.log_in(code=token, to_file=user_secret, scopes=scopes)

        except Exception:

            print("Sadly, that did not work. On some sites, this login mechanism")
            print("(namely OAuth) seems to be broken. There is an alternative")
            print("if you are willing to trust us with your password just this")
            print("once. We need it just this once in order to get an access")
            print("token. We won't save it. If you don't want to try this, use")
            print("Ctrl+C to quit. If you want to try it, please provide your")
            print("login details.")

            sys.stdout.write("Email: ")
            sys.stdout.flush()
            email = sys.stdin.readline().rstrip()
            sys.stdout.write("Password: ")
            sys.stdout.flush()
            password = sys.stdin.readline().rstrip()

            # on the very first login, --pace has no effect
            mastodon.log_in(
                username=email,
                password=password,
                to_file=user_secret,
                scopes=scopes
            )

        return mastodon

    def deauthorize(self):
        """
        Deauthorize by deleting the file containing the authorization token.
        """
        user_secret = self.user_secret
        client_secret = self.client_secret
        if os.path.isfile(user_secret):
            os.remove(user_secret)
        if os.path.isfile(client_secret):
            os.remove(client_secret)

    def login(self, pace=False):
        """
        Register app, authorize and return an instance of ``Mastodon``
        """
        url = self.url
        client_secret = self.client_secret
        user_secret = self.user_secret

        if not os.path.isfile(client_secret):
            self.register()

        if not os.path.isfile(user_secret):
            mastodon = self.authorize()

        else:

            if pace:

                # in case the user kept running into a General API problem
                mastodon = Mastodon(
                    client_id=client_secret,
                    access_token=user_secret,
                    api_base_url=url,
                    ratelimit_method="pace",
                    ratelimit_pacefactor=0.9,
                    request_timeout=300
                )

            else:

                # the defaults are ratelimit_method='wait',
                # ratelimit_pacefactor=1.1, request_timeout=300
                mastodon = Mastodon(
                    client_id=client_secret,
                    access_token=user_secret,
                    api_base_url=url
                )

        return mastodon

def load(file_name, required=False, quiet=False, combine=False):
    """
    Load the JSON data from a file.
    """

    if required and not os.path.isfile(file_name):
        print("You need to create an archive, first", file=sys.stderr)
        sys.exit(2)

    if os.path.isfile(file_name) and os.path.getsize(file_name) > 0:

        def _json_load(fname):
            if not quiet:
                print("Loading existing archive:", fname)

            with open(fname, mode='r', encoding='utf-8') as fp:
                return json.load(fp)

        data = _json_load(file_name)
        if combine:
            # Load latest archive first to keep chronological order
            archives = list(
                reversed(glob.glob(file_name.replace(".json", ".*.json")))
            )

            if required and not quiet and not archives:
                print("Warning: No split archives to combine", file=sys.stderr)

            # Merge dictionaries loaded from JSON archives
            for archive in archives:
                archived_data = _json_load(archive)

                for collection in ["statuses", "favourites", "mentions"]:
                    data[collection].extend(archived_data[collection])

        return data

    return None

def save(file_name, data):
    """
    Save the JSON data in a file. If the file exists, rename it,
    just in case.
    """
    date_handler = lambda obj: (
        obj.isoformat()
        if isinstance(obj, (datetime.datetime, datetime.date))
        else None)

    if os.path.isfile(file_name):
        backup_file = file_name + '~'
        print("Backing up", file_name, "to", backup_file)
        if os.path.isfile(backup_file):
            ans = ""
            while ans.lower() not in ("y", "n", "yes", "no"):
                ans = input(
                    "Backup: {} exists! Overwrite (yes/no)? ".format(backup_file)
                )

            if ans.lower()[0] == "y":
                shutil.copy2(file_name, backup_file)
            else:
                print("Exiting to avoid overwriting backup.", file=sys.stderr)
                sys.exit(0)

    with open(file_name, mode = 'w', encoding = 'utf-8') as fp:
        data = json.dump(data, fp, indent = 2, default = date_handler)

def all_accounts():
    """
    Return all the known user accounts in the current directory.
    """
    archives = glob.glob('*.user.*.json');
    if not archives:
        print("You need to create an archive, first", file=sys.stderr)
        sys.exit(2)
    else:
        users = []
        for archive in archives:
            m = re.match(r"(.*)\.user\.(.*)\.json", archive)
            if m:
                users.append("%s@%s" % m.group(2, 1))
        return users

def keep(statuses, weeks):
    """
    Return all statuses newer than some weeks
    """

    delta = datetime.timedelta(weeks = weeks)
    cutoff = datetime.datetime.today() - delta

    def matches(status):
        created = datetime.datetime.strptime(status["created_at"][0:10], "%Y-%m-%d")
        return created >= cutoff

    return list(filter(matches, statuses))

def whitelist(domain, username):
    file_name = domain + '.user.' + username + '.whitelist.txt'
    whitelist = set()
    if os.path.isfile(file_name):
        with open(file_name, mode = 'r', encoding = 'utf-8') as fp:
            for line in fp:
                # kensanata
                # kensanata@dice.camp
                # Alex Schroeder <kensanata@dice.camp>
                m = re.search(r"([a-zA-Z0-9.-]+@[a-zA-Z0-9.-]+)", line)
                if not m:
                    m = re.search(r"([a-zA-Z0-9.-]+)", line)
                if m:
                    whitelist.add(m.group(1))
        print("%d accounts are on the whitelist" % len(whitelist))
    else:
        print("There is no whitelist")
    return whitelist
