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
import math
from datetime import timedelta, datetime
from . import core

def split(args):
    """
    Split older toots into a new file
    """

    confirmed = args.confirmed

    if not confirmed:

        print("This is a dry run and nothing will be moved.\n"
              "Instead, we'll just list what would have happened.\n"
              "Use --confirmed to actually do it.")

    (username, domain) = args.user.split('@')

    status_file = domain + '.user.' + username + '.json'
    data = core.load(status_file, required = True)
    older_data = {}

    n = 0
    older_status_file = ''
    while True:
        older_status_file = domain + '.user.' + username + '.' + str(n) + '.json'
        if os.path.exists(older_status_file):
            n = n + 1
        else:
            break

    delta = timedelta(weeks = args.weeks)
    cutoff = datetime.today() - delta

    print("Older than " + str(cutoff))

    n_statuses = 0

    for collection in ["statuses",
                       "favourites",
                       "mentions"]:
        statuses = list(filter(
            lambda status: datetime.strptime(status["created_at"][0:10], "%Y-%m-%d") >= cutoff,
            data[collection]))
        older_statuses = list(filter(
            lambda status: datetime.strptime(status["created_at"][0:10], "%Y-%m-%d") < cutoff,
            data[collection]))

        data[collection] = statuses
        older_data[collection] = older_statuses

        moved = len(older_statuses)
        print(collection + ": " + str(moved))
        n_statuses += moved

    if confirmed and n_statuses > 0:

        print("Saving " + status_file)
        core.save(status_file, data)
        print("Saving " + older_status_file)
        core.save(older_status_file, older_data)

    elif confirmed:

        print("No older statuses to move")

    else:

        print("Would have saved this to " + older_status_file)
