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
        account = status["account"]
        emojis = status["emojis"]
        reactions = status.get("reactions", [])
        card = status["card"]
        if status["reblog"] is not None:
            attachments = status["reblog"]["media_attachments"]
            account = status["reblog"]["account"]
            emojis = status["reblog"]["emojis"]
            card = status["reblog"]["card"]
        for attachment in attachments:
                if attachment["preview_url"]:
                        urls.append((attachment["preview_url"], attachment["preview_remote_url"]))
                        preview_urls_count += 1
                if attachment["url"]:
                        urls.append((attachment["url"], attachment["remote_url"]))
        if account["avatar"]:
                urls.append((account["avatar"], None))
        for emoji in emojis:
                if emoji["url"]:
                        urls.append((emoji["url"], None))
        if len(account["emojis"]) > 0:
            for emoji in account["emojis"]:
                if emoji["url"]:
                        urls.append((emoji["url"], None))
        for reaction in reactions:
                if "url" in reaction and reaction["url"]  :
                        urls.append((reaction["url"], None))
        if card and card["image"]:
                urls.append((card["image"], None))

    urls = list(dict.fromkeys(urls))

    # these two are always available; if the user didn't set it, will link to a
    # placeholder image
    for picture in ["avatar", "header"]:
        urls.append((data["account"][picture], None))

    if not args.quiet:
        print("%d urls in your backup (%d are previews)" % (len(urls), preview_urls_count))

    if not args.quiet:
        bar = Bar('Downloading', max = len(urls))

    errors = 0

    # start downloading the missing files from the back
    for url in reversed(urls):
        remoteurl = url[1]
        url = url[0]
        if not args.quiet:
            bar.next()
        path = urlparse(url).path
        file_name = media_dir + path
        if not os.path.isfile(file_name):
            dir_name =  os.path.dirname(file_name)
            os.makedirs(dir_name, exist_ok = True)
            try:
                download(url, remoteurl, file_name, args)
            except OSError as e:
                print("\n" + e.msg + ": " + url, file=sys.stderr)
                errors += 1
            if pace:
                time.sleep(1)

    if not args.quiet:
        bar.finish()

    if errors > 0:
        print("%d downloads failed" % errors)

def download(url, remoteurl, file_name, args):
    req = urllib.request.Request(
        url, data=None,
        headers={'User-Agent': 'Mastodon-Archive/1.3 '
                    '(+https://github.com/kensanata/mastodon-archive#mastodon-archive)'})
    retries = 5
    retry_downloads = True
    while retries > 0 and retry_downloads:
        try:
            with urllib.request.urlopen(req) as response, open(file_name, 'wb') as fp:
                data = response.read()
                fp.write(data)
                retry_downloads = False
        except HTTPError as he:
            if not args.suppress_errors:
                print("\nFailed to open " + url + " during a media request.")
                if remoteurl:
                    download(remoteurl, None, file_name, args)
            if he.status == 429:
                print("Delaying next requests...")
                time.sleep(3*60)
                retries -= 1
            else:
                retry_downloads = False
                if remoteurl:
                    download(remoteurl, None, file_name, args)
        except URLError as ue:
            if not args.suppress_errors:
                print("\nFailed to open " + url + " during a media request.")
                if remoteurl:
                    download(remoteurl, None, file_name, args)
            retry_downloads = False
