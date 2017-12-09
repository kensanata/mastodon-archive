#!/usr/bin/env python3
# Copyright (C) 2017  Alex Schroeder <alex@gnu.org>

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
    return login(args, scopes = ['read', 'write'])

def deauthorize(args):
    """
    Deauthorize the account. We do this by deleting the file
    containing the authorization token.
    """
    (username, domain) = args.user.split("@")
    user_secret = domain + '.user.' + username + '.secret'
    if os.path.isfile(client_secret):
        os.remove(user_secret)
    
def login(args, scopes = ['read']):
    """
    Login to your Mastodon account
    """

    pace = args.pace
    
    (username, domain) = args.user.split("@")

    url = 'https://' + domain
    client_secret = domain + '.client.secret'
    user_secret = domain + '.user.' + username + '.secret'
    mastodon = None
        
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
            scopes=scopes)

        print("Visit the following URL and authorize the app:")
        print(url)

        print("Then paste the access token here:")
        token = sys.stdin.readline().rstrip()

        # on the very first login, --pace has no effect
        mastodon.log_in(
            username = username,
            code = token,
            to_file = user_secret,
            scopes=scopes)

    else:

        if pace:
            
            # in case the user kept running into a General API problem
            mastodon = Mastodon(
                client_id = client_secret,
                access_token = user_secret,
                api_base_url = url,
                ratelimit_method='pace',
                ratelimit_pacefactor=0.9,
                request_timeout=300)
            
        else:
            
            # the defaults are ratelimit_method='wait',
            # ratelimit_pacefactor=1.1, request_timeout=300
            mastodon = Mastodon(
                client_id = client_secret,
                access_token = user_secret,
                api_base_url = url)

    return mastodon
