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
import json
import html2text
import re

argv = sys.argv

if len(argv) < 2:
    print("Usage: %s username@instance [patterns...]" % argv[0], file=sys.stderr)
    sys.exit(1)

(username, domain) = argv[1].split('@')

patterns = argv[2:]

status_file = domain + '.user.' + username + '.json'

if not os.path.isfile(status_file):

    print("You need to run mastodon-backup.py, first", file=sys.stderr)
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
    
if len(patterns) > 0:
    data["statuses"] = list(filter(matches, data["statuses"]))
    
for status in data["statuses"]:
    if status["reblog"] is not None:
        print("%s boosted" % status["account"]["display_name"])
        status = status["reblog"]
    print("%s @%s %s" % (
        status["account"]["display_name"],
        status["account"]["username"],
        status["created_at"]))
    print(html2text.html2text(status["content"]))
