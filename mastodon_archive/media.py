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

import datetime
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

DEFAULT_PACE = 1
paces_file = 'host_paces.txt'
hosts_paces = {}
# The first time in a run we decide we need to increase the pace for a host, we
# save the new pace here. If we increase it again later in the same run, we
# _don't_ save it here. This is because the first time in a run we hit the rate
# limit, it's likely that we were starting from a blank slate, whereas if we
# hit it again in the same run we were probably cut off prematurely due to our
# earlier requests. Our goal is for the paces stored in the pace file to be
# our best guess of what the lowest possible delay between requests needs to be
# to avoid rate-limiting entirely.
hosts_paces_first = {}
hosts_raced = {}
hosts_paced = {}

class RateLimitException(Exception):
    def __init__(self, host):
        self.host = host


def media(args):
    """
    Download all the media files linked to from your archive
    """

    if args.pace:
        read_paces_file()

    (username, domain) = args.user.split('@')

    status_file = domain + '.user.' + username + '.json'
    media_dir = domain + '.user.' + username
    data = core.load(status_file, required=True, quiet=True, combine=args.combine)

    urls = {}
    preview_urls_count = 0

    for collection in (args.collection or args.collection_default):
        for status in data[collection]:
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
                    tuple = (attachment["preview_url"],
                             attachment["preview_remote_url"])
                    if tuple not in urls:
                        urls[tuple] = 1
                        preview_urls_count += 1
                    if attachment["url"]:
                        urls[(attachment["url"], attachment["remote_url"])] = 1
            if account["avatar"]:
                urls[(account["avatar"], None)] = 1
            for emoji in emojis:
                if emoji["url"]:
                    urls[(emoji["url"], None)] = 1
            if len(account["emojis"]) > 0:
                for emoji in account["emojis"]:
                    if emoji["url"]:
                        urls[(emoji["url"], None)] = 1
            for reaction in reactions:
                if "url" in reaction and reaction["url"]:
                    urls[(reaction["url"], None)] = 1
            if card and card["image"]:
                urls[(card["image"], None)] = 1

    # these two are always available; if the user didn't set it, will link to a
    # placeholder image
    for picture in ["avatar", "header"]:
        urls[(data["account"][picture], None)] = 1

    urls = list(urls.keys())

    if not args.quiet:
        print("%d urls in your backup (%d are previews)" % (len(urls), preview_urls_count))

    urls = ((url, remoteurl, media_dir + urlparse(url).path)
            for url, remoteurl in urls)
    urls = [(url, remoteurl, file_name)
            for url, remoteurl, file_name in urls
            if not os.path.isfile(file_name) and
            not os.path.isfile(f"{file_name}.missing")]

    errors = 0
    retries = 5

    # downloading the missing files from the back
    new_queue = list(reversed(urls))
    while new_queue:
        queue = new_queue
        new_queue = []
        rate_limit_exceptions = {}
        succeeded = 0

        if not args.quiet:
            print(f"{len(queue)} to download")
            bar = Bar('Downloading', max = len(queue))

        for url, remoteurl, file_name in queue:
            if not args.quiet:
                bar.next()
            path = urlparse(url).path
            dir_name =  os.path.dirname(file_name)
            try:
                os.makedirs(dir_name, exist_ok = True)
                if download(url, remoteurl, file_name, args):
                    succeeded += 1
                else:
                    errors += 1
            except RateLimitException as rle:
                rate_limit_exceptions[rle.host] = 1
                new_queue.append((url, remoteurl, file_name))
            except OSError as e:
                print("\n" + str(e) + ": " + url, file=sys.stderr)
                errors += 1

        if new_queue:
            if succeeded:
                retries = 5
            else:
                retries -= 1
                if retries < 1:
                    if not args.suppress_errors:
                        print(f'\nGiving up after 5 retries')
                    break
                
            now = time.time()
            next_time = min((hosts_raced.get(h, now)
                             for h in rate_limit_exceptions))
            if next_time > now:
                wait_time = next_time - now
                if not args.suppress_errors:
                    print(f'\nWaiting {wait_time:.0f} seconds for rate limits to expire')
                time.sleep(wait_time)
        else:
            if not args.quiet:
                bar.finish()


    if not args.suppress_errors and errors > 0:
        print("%d downloads failed" % errors)


def download(url, remoteurl, file_name, args, from404=True):
    req = urllib.request.Request(
        url, data=None,
        headers={'User-Agent': 'Mastodon-Archive/1.3 '
                    '(+https://github.com/kensanata/mastodon-archive#mastodon-archive)'})
    
    if req.host in hosts_raced:
        if time.time() < hosts_raced[req.host]:
            raise RateLimitException(req.host)
        hosts_raced.pop(req.host)

    if args.pace:
        if req.host not in hosts_paces:
            hosts_paces[req.host] = DEFAULT_PACE
        elif req.host in hosts_paced:
            time.sleep(max(0, hosts_paced[req.host] - time.time()))
        hosts_paced[req.host] = time.time() + hosts_paces[req.host]

    try:
        with urllib.request.urlopen(req) as response, open(file_name, 'wb') as fp:
            data = response.read()
            fp.write(data)
        # On success, clear any history maintained by `check_if_permanent_error`
        try:
            os.remove(f"{file_name}.errors")
        except FileNotFoundError:
            pass  # error file often won't exist
        return True
    except HTTPError as he:
        if not args.suppress_errors:
            print("\nFailed to open " + url + " during a media request.")

        if he.status == 429:
            if not args.suppress_errors:
                print(f'\nDelaying next request to {req.host}')
            if args.pace:
                # Slow down the pace for this host because we're apparently not
                # waiting long enough to avoid its rate-limiting
                hosts_paces[req.host] *= 1.1
                if req.host not in hosts_paces_first:
                    hosts_paces_first[req.host] = hosts_paces[req.host]
                    write_paces_file()
            if reset := he.headers['x-ratelimit-reset']:
                hosts_raced[req.host] = \
                    datetime.datetime.fromisoformat(reset).timestamp()
            else:
                hosts_raced[req.host] = time.time() + 3*60
            raise RateLimitException(req.host)

        # We stop trying to download 401, 403, and 404 because 401 and 403
        # almost always means the server has authorized fetch enabled
        # and we're never going to be able to download.
        if remoteurl:
            return download(remoteurl, None, file_name, args,
                            from404=he.status in (401, 403, 404))

        if from404 and he.status in (401, 403, 404):
            flag = f"{file_name}.missing"
            if not args.suppress_errors:
                print(f"\nSuppressing future downloads with {flag}.")
            open(flag, "wb").close()
            return False

        check_if_permanent_error(url, file_name, he, args)
        return False
    except URLError as ue:
        if not args.suppress_errors:
            print("\nFailed to open " + url + " during a media request.")
        if remoteurl:
            return download(remoteurl, None, file_name, args)
        check_if_permanent_error(url, file_name, ue, args)
        return False


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


def read_paces_file():
    if not os.path.exists(paces_file):
        return
    with open(paces_file) as f:
        for line in f:
            (host, pace) = line.strip().split(':', 1)
            hosts_paces[host] = float(pace)


def write_paces_file():
    if not hosts_paces_first:
        return
    new_file = f'{paces_file}.new'
    paces = dict(hosts_paces)
    paces.update(hosts_paces_first)
    with open(new_file, 'w') as f:
        for host, pace in paces.items():
            if pace == DEFAULT_PACE:
                continue
            print(f'{host}:{pace}', file=f)
    os.rename(new_file, paces_file)
