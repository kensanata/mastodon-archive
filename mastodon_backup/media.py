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
import os
import json
from pySmartDL import SmartDL
from progress.bar import Bar
from urllib.parse import urlparse
from time import sleep
from urllib.error import HTTPError

def media(args):
    """
    Download all the media files linked to from your archive
    """

    (username, domain) = args.user.split('@')

    status_file = domain + '.user.' + username + '.json'
    media_dir = domain + '.user.' + username

    if not os.path.isfile(status_file):

        print("You need to create an archive, first", file=sys.stderr)
        sys.exit(2)

    with open(status_file, mode = 'r', encoding = 'utf-8') as fp:
        data = json.load(fp)

    urls = []
    for status in data["statuses"]:
        attachments = status["media_attachments"]
        if status["reblog"] is not None:
            attachments = status["reblog"]["media_attachments"]
        for attachment in attachments:
                for url in [attachment["preview_url"], attachment["url"]]:
                        urls.append(url)

    print("%d urls in your backup (half of them are previews)" % len(urls))

    bar = Bar('Downloading', max = len(urls))

    errors = 0

    downloaders = []
    for url in urls:
        bar.next()
        path = urlparse(url).path
        if not os.path.isfile(media_dir + path):
            download = SmartDL(url,
                               dest = media_dir + path,
                               progress_bar = None)
            try:
                download.start(blocking = False)
                downloaders.append(download)
            except HTTPError as e:
                # print("\n" + e.msg + ": " + url, file=sys.stderr)
                errors += 1

    bar.finish()

    if errors > 0:
        print("%d downloads failed" % errors)
