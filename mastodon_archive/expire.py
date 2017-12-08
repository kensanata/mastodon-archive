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
import json
from progress.bar import Bar
from datetime import timedelta, datetime


def expire(args):
    """
    Expire toots: delete toots and unfavour favourites older than a few weeks
    """

    collection = args.collection

    (username, domain) = args.user.split('@')

    status_file = domain + '.user.' + username + '.json'
    
    if not os.path.isfile(status_file):

        print("You need to create an archive, first", file=sys.stderr)
        sys.exit(2)

    with open(status_file, mode = 'r', encoding = 'utf-8') as fp:
        data = json.load(fp)

    delta = timedelta(weeks = args.weeks)
    cutoff = datetime.today() - delta

    def matches(status):
        created = datetime.strptime(status["created_at"][0:10], "%Y-%m-%d")
        return created < cutoff

    statuses = list(filter(matches, data[collection]))

    if (len(statuses) == 0):
        print("No statuses are older than %d weeks" % args.weeks,
              file=sys.stderr)
        sys.exit(3)

    bar = Bar('Expiring', max = len(statuses))

    for status in statuses:
        bar.next()
        if collection == 'statuses':
            mastodon.delete(status["id"]);
            # print ("Delete %s: %s" % (status["id"], status["created_at"]))
        elif collection == 'favourites':
            mastodon.unfavourite(status["reblog"]["id"])
            # print ("Unfavour %s: %s" % (status["id"], status["created_at"]))

    bar.finish()
