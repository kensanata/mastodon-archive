#!/usr/bin/env python3
# Copyright (C) 2017-2018  Alex Schroeder <alex@gnu.org>
# Copyright (C) 2017       Steve Ivy <steveivy@gmail.com>

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

def login(args):
    """
    Just login to your Mastodon account
    """

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

    print("Login OK")
