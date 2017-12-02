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
import html2text
import re

def text(args):
    """
    Convert toots to plain text, optionally filtering them
    """

    collection = args.collection
    reverse = args.reverse
    patterns = args.pattern

    (username, domain) = args.user.split('@')

    status_file = domain + '.user.' + username + '.json'

    if not os.path.isfile(status_file):

        print("You need to create an archive, first", file=sys.stderr)
        sys.exit(2)

    with open(status_file, mode = 'r', encoding = 'utf-8') as fp:
        data = json.load(fp)

    def matches(status):
        if status["reblog"] is not None:
            status = status["reblog"]
        for pattern in patterns:
            found = False
            for s in [status["content"],
                      status["account"]["display_name"],
                      status["account"]["username"],
                      status["created_at"]]:
                if re.search(pattern,s) is not None:
                    found = True
                    continue
            if not found:
                return False
        return True

    statuses = data[collection]

    if len(patterns) > 0:
        statuses = list(filter(matches, statuses))

    if reverse:
        statuses = reversed(statuses)

    for status in statuses:
        str = '';
        if status["reblog"] is not None:
            str += ("%s boosted" % status["account"]["display_name"])
            status = status["reblog"]
        str += ("%s @%s %s" % (
            status["account"]["display_name"],
            status["account"]["username"],
            status["created_at"]))
        str += (status["url"])
        str += html2text.html2text(status["content"])
        # This forces UTF-8 independent of terminal capabilities, thus
        # avoiding problems with LC_CTYPE=C and other such issues.
        # This works well when redirecting output to a file, which
        # will then be an UTF-8 encoded file.
        sys.stdout.buffer.write(str.encode('utf-8'))
