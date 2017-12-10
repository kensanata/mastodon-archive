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

import sys
import os.path
from . import core

def boosts(list):
    """
    Count boosts in list of statuses
    """
    i = 0
    for item in list:
        if item["reblog"] is not None:
            i += 1
    return i

def report(args):
    """
    Report on your toots and favourites
    """

    (username, domain) = args.user.split('@')

    status_file = domain + '.user.' + username + '.json'
    data = core.load(status_file, required = True, quiet = True)

    if "statuses" in data:
        print("Statuses:   %10d" % len(data["statuses"]))
        print("Boosts:     %10d" % boosts(data["statuses"]))

    if "favourites" in data:
        print("Favourites: %10d" % len(data["favourites"]))
