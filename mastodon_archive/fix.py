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
from . import core

def fix_boosts(args):
    """
    Go through all the boosts and mark them as undeleted.
    """

    confirmed = args.confirmed

    if not confirmed:

        print("This is a dry run and nothing will be changed.\n"
              "Instead, we'll just list what would have happened.\n"
              "Use --confirmed to actually do it.")

    (username, domain) = core.parse(args.user)

    status_file = domain + '.user.' + username + '.json'
    data = core.load(status_file, required=True, combine=args.combine)
    n = 0

    for status in data["statuses"]:
        if status["reblog"] and "deleted" in status and status["deleted"]:
            del status["deleted"]
            n = n + 1
            if n == 1 and not confirmed:
                print("Some examples:")
            if n <= 20 and not confirmed:
                print(str(n) + " " + status["reblog"]["url"])

    if confirmed and n > 0:

        print("Saving updated data to", status_file)
        core.save(status_file, data)

    elif confirmed:

        print("No boosted statuses were undeleted")

    else:

        print("Would have marked " + str(n) + " statuses as not deleted")
