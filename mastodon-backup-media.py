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
import os
import json
from pySmartDL import SmartDL
from progress.bar import Bar
from urllib.parse import urlparse
from time import sleep

argv = sys.argv

if len(argv) != 2:
    print("Usage: %s username@instance" % argv[0], file=sys.stderr)
    sys.exit(1)

(username, domain) = argv[1].split('@')

status_file = domain + '.user.' + username + '.json'
media_dir = domain + '.user.' + username

if not os.path.isfile(status_file):

    print("You need to run mastodon-backup.py, first", file=sys.stderr)
    sys.exit(2)

with open(status_file, mode = 'r', encoding = 'utf-8') as fp:
    data = json.load(fp)

urls = []
for status in data["statuses"]:
    for media in status["media_attachments"]:
        for url in [media["preview_url"], media["url"]]:
            urls.append(url)

print("%d urls in your backup (half of them are previews)" % len(urls))
            
downloaders = []
for url in urls:
    path = urlparse(url).path
    if not os.path.isfile(media_dir + path):
        download = SmartDL(url,
                           dest = media_dir + path,
                           progress_bar = None)
        download.start()
        downloaders.append(download)

print("%d files already exist" % (len(urls) - len(downloaders)))

bar = Bar('Downloading', max = len(downloaders))

errors = 0
while len(downloaders) > 0:
    sleep(1)
    done = []
    for download in downloaders:
        if download.isFinished():
            done.append(download)
            bar.next()
            if not download.isSuccessful():
                errors += 1
    for download in done:
        downloaders.remove(download)

bar.finish()

if errors > 0:
    print("%d downloads failed: " + errors)
