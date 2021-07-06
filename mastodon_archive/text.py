#!/usr/bin/env python3
# Copyright (C) 2017-2018  Alex Schroeder <alex@gnu.org>
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

import itertools
import sys
import os.path
import html2text
import re
from . import core
from urllib.parse import urlparse

def text(args):
    """
    Convert toots to plain text, optionally filtering them
    """

    collection = args.collection
    reverse = args.reverse
    patterns = args.pattern
    combine = args.combine

    (username, domain) = core.parse(args.user)

    media_dir = domain + '.user.' + username
    status_file = domain + '.user.' + username + '.json'
    data = core.load(status_file, required=True, quiet=True, combine=combine)

    def matches(status):
        if status["reblog"] is not None:
            status = status["reblog"]
        for pattern in patterns:
            found = False
            for s in [status["content"],
                      status["account"]["display_name"],
                      status["account"]["username"],
                      status["created_at"]]:
                if re.search(pattern, s, flags=re.IGNORECASE) is not None:
                    found = True
                    continue
            if not found:
                return False
        return True

    if collection == "all":
        statuses = itertools.chain.from_iterable(
            data[collection] for collection in ["statuses", "favourites", "mentions"]
        )
    else:
        statuses = data[collection]

    if len(patterns) > 0:
        statuses = list(filter(matches, statuses))

    statuses = sorted(statuses, reverse=reverse, key=lambda status: status["created_at"])

    for status in statuses:
        str = '';
        if status["reblog"] is not None:
            str += (status["account"]["display_name"] + "boosted\n")
            status = status["reblog"]
        str += ("%s @%s %s\n" % (
            status["account"]["display_name"],
            status["account"]["username"],
            status["created_at"]))
        str += "🔗 " + status["url"] + "\n"
        str += html2text.html2text(status["content"]).strip() + "\n"
        for attachment in status["media_attachments"]:
            # should we check attachment["preview_url"] as well?
            for url in [attachment["url"]]:
                path = urlparse(url).path
                file_name = media_dir + path
                if os.path.isfile(file_name):
                    str += "🖻 " + file_name + "\n"
                elif url not in str:
                    str += "🔗 " + url + "\n"
        str += "\n"
        # This forces UTF-8 independent of terminal capabilities, thus
        # avoiding problems with LC_CTYPE=C and other such issues.
        # This works well when redirecting output to a file, which
        # will then be an UTF-8 encoded file.
        sys.stdout.buffer.write(str.encode('utf-8'))
