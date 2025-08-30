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

import itertools
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

    urls = ((url, remoteurl, media_dir + urlparse(url).path)
            for url, remoteurl in urls)
    urls = [(url, remoteurl, file_name)
            for url, remoteurl, file_name in urls
            if not os.path.isfile(file_name) and
            not os.path.isfile(f"{file_name}.missing")]

    if not args.quiet:
        print(f"{len(urls)} to download")
        bar = Bar('Downloading', max = len(urls))

    errors = 0

    # start downloading the missing files from the back
    for url, remoteurl, file_name in reversed(urls):
        if not args.quiet:
            bar.next()
        path = urlparse(url).path
        dir_name =  os.path.dirname(file_name)
        os.makedirs(dir_name, exist_ok = True)
        try:
            download(url, remoteurl, file_name, args)
        except OSError as e:
            print("\n" + str(e) + ": " + url, file=sys.stderr)
            errors += 1
        if pace:
            time.sleep(1)

    if not args.quiet:
        bar.finish()

    if errors > 0:
        print("%d downloads failed" % errors)

def download(url, remoteurl, file_name, args, from404=True):
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
                # We stop trying to download both 401 and 404 because 401
                # almost always means the server has authorized fetch enabled
                # and we're never going to be able to download.
                if remoteurl:
                    return download(remoteurl, None, file_name, args,
                                    from404=he.status in (401, 404))
                if from404 and he.status in (401, 404):
                    flag = f"{file_name}.missing"
                    if not args.suppress_errors:
                        print(f"\nSuppressing future downloads with {flag}.")
                    open(flag, "wb").close()
            if he.status == 429:
                print("Delaying next requests...")
                time.sleep(3*60)
                retries -= 1
            else:
                retry_downloads = False
                if remoteurl:
                    download(remoteurl, None, file_name, args)
                check_if_permanent_error(url, file_name, he, args)
        except URLError as ue:
            if not args.suppress_errors:
                print("\nFailed to open " + url + " during a media request.")
                if remoteurl:
                    download(remoteurl, None, file_name, args)
            retry_downloads = False
            check_if_permanent_error(url, file_name, ue, args)

def check_if_permanent_error(url, file_name, error, args):
    """
    Record a download error for this media and possibly suppress further attempts.

    Suppression occurs if the same error has been observed on all attempts for
    at least two weeks.
    """
    error_string = repr(error)
    errors_path = f"{file_name}.errors"

    add_entry = {'timestamp': time.time(), 'url': url, 'error': error_string}
    with open(errors_path, 'a') as f:
        f.write(json.dumps(add_entry, indent=None, sort_keys=True) + '\n')

    # Check if we now have a streak of identical errors.

    with open(errors_path, 'r') as f:
        entries = [json.loads(entry) for entry in f.readlines()]

    # The same media file *could* have multiple URLs, so we'll only
    # look at failures for the current URL. (As of 2025-08-30, the
    # `download` function effectively only calls this check for the
    # remote URL, but that could change in the future.) We'll also
    # look the entries in reverse chrono order.
    recent_entries = [e for e in reversed(entries) if e['url'] == url]
    latest_error = recent_entries[0]['error']
    streak = list(itertools.takewhile(lambda e: e['error'] == error_string, recent_entries))
    streak_days = (streak[0]['timestamp'] - streak[-1]['timestamp']) / 86400

    if streak_days >= 14:
        flag = f"{file_name}.missing"
        if not args.suppress_errors:
            print(f"\nSuppressing future downloads with {flag} due to repeated failures.")
        open(flag, "wb").close()
