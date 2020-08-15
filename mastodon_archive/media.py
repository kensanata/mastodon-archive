#!/usr/bin/env python3
# Copyright (C) 2017–2019  Alex Schroeder <alex@gnu.org>
# Copyright (C) 2017       Steve Ivy <steveivy@gmail.com>

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

import os
import sys
import json
import time
import urllib.request
from urllib.error import HTTPError
from urllib.error import URLError
from progress.bar import Bar
from urllib.parse import urlparse
from . import core

def media(args):
    """
    Download all the media files linked to from your archive
    """

    pace = hasattr(args, 'pace') and args.pace

    (username, domain) = args.user.split('@')

    status_file = domain + '.user.' + username + '.json'
    media_dir = domain + '.user.' + username
    data = core.load(status_file, required=True, quiet=True, combine=args.combine)

    urls = []
    preview_urls_count=0
    for status in data[args.collection]:
        attachments = status["media_attachments"]
        if status["reblog"] is not None:
            attachments = status["reblog"]["media_attachments"]
        for attachment in attachments:
                if attachment["preview_url"]:
                        urls.append(attachment["preview_url"])
                        preview_urls_count += 1
                if attachment["url"]:
                        urls.append(attachment["url"])

    print("%d urls in your backup (%d are previews)" % (len(urls), preview_urls_count))

    bar = Bar('Downloading', max = len(urls))

    errors = 0

    # start downloading the missing files from the back
    for url in reversed(urls):
        bar.next()
        path = urlparse(url).path
        file_name = media_dir + path
        if not os.path.isfile(file_name):
            dir_name =  os.path.dirname(file_name)
            os.makedirs(dir_name, exist_ok = True)
            try:
                req = urllib.request.Request(
                    url, data=None,
                    headers={'User-Agent': 'Mastodon-Archive/1.3 '
                             '(+https://github.com/kensanata/mastodon-backup#mastodon-archive)'})
                try:
                  with urllib.request.urlopen(req) as response, open(file_name, 'wb') as fp:
                    data = response.read()
                    fp.write(data)
                except HTTPError as he:
                  print("\nFailed to open " + url + " during a media request.")
                except URLError as ue:
                  print("\nFailed to open " + url + " during a media request.")
            except OSError as e:
                print("\n" + e.msg + ": " + url, file=sys.stderr)
                errors += 1
            if pace:
                time.sleep(1)

    bar.finish()

    if errors > 0:
        print("%d downloads failed" % errors)
