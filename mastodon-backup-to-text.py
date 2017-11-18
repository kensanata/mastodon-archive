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

argv = sys.argv

if len(argv) != 2:
    print("Usage: %s username@instance" % argv[0])
    sys.exit(1)

(username, domain) = argv[1].split('@')

status_file = domain + '.user.' + username + '.json'

if not os.path.isfile(status_file):

    print("You need to run mastodon-backup.py, first")
    sys.exit(2)

with open(status_file, mode = 'r', encoding = 'utf-8') as fp:
    statuses = json.load(fp)
    fp.close()

for status in statuses:
    if status["reblog"] is not None:
        print("%s boosted" % status["account"]["display_name"])
        status = status["reblog"]
    print("%s @%s %s" % (
        status["account"]["display_name"],
        status["account"]["username"],
        status["created_at"]))
    print(html2text.html2text(status["content"]))
