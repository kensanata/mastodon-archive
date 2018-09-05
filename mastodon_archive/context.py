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
import os.path
import html2text
import re
from . import core

class Found(Exception): pass

def context(args):
    """
    Show the context of a toot: ancestors, the toot itself, and descendants
    """

    url = args.url

    (username, domain) = core.parse(args.user)

    status_file = domain + '.user.' + username + '.json'
    data = core.load(status_file, required = True, quiet = True)

    found = None;
    index = {} # mapping ids to statuses
    children = {} # mapping ids to list of children ids

    for collection in ["statuses",
                       "favourites",
                       "mentions"]:
        statuses = data[collection];
        print("Indexing %d %s..." % (len(statuses), collection))
        for status in statuses:

            if status["reblog"] is not None:
                status = status["reblog"]

            # only accept one status per id
            if status["id"] in index:
                pass
                # print("Warning: duplicate id %s" % status["id"], file=sys.stderr)
            else:
                index[status["id"]] = status
                if "in_reply_to_id" in status:
                    if status["in_reply_to_id"] not in children:
                        children[status["in_reply_to_id"]] = [status["id"]]
                    else:
                        children[status["in_reply_to_id"]].append(status["id"])

            for u in [status["uri"],
                      status["url"]]:
                if u == url:
                    found = status
                    # don't break, we want to index them all

    if not found:
        print("The URL/URI was not found", file=sys.stderr)
        sys.exit(5)

    result = [found]

    # add ancestors
    id = found["in_reply_to_id"]

    while id in index:
        status = index[id];
        result.insert(0, status)
        id = status["in_reply_to_id"]

    # add descendants
    try:
        ids = children[found["id"]]
        print(ids)
        while ids:
            id = ids.pop(0)
            result.append(index[id])
            if id in children:
                ids.extend(children[id])
    except:
        if not result:
            print("The status at the provided URL/URI had no context in your archive", file=sys.stderr)
            sys.exit(5)

    for status in result:
        str = '';
        if status["reblog"] is not None:
            str += (status["account"]["display_name"] + "boosted\n")
            status = status["reblog"]
        str += ("%s @%s %s\n" % (
            status["account"]["display_name"],
            status["account"]["username"],
            status["created_at"]))
        str += status["url"] + "\n"
        str += html2text.html2text(status["content"])
        # This forces UTF-8 independent of terminal capabilities, thus
        # avoiding problems with LC_CTYPE=C and other such issues.
        # This works well when redirecting output to a file, which
        # will then be an UTF-8 encoded file.
        sys.stdout.buffer.write(str.encode('utf-8'))
