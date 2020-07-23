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
import textwrap
import unicodedata
from . import core

def boosts(statuses):
    """
    Count boosts in statuses
    """
    i = 0
    for item in statuses:
        if item["reblog"] is not None:
            i += 1
    return i

def media(statuses):
    """
    Count media attachments in statuses
    """
    i = 0
    for item in statuses:
        i += len(item["media_attachments"])
    return i


def tags(statuses, include_boosts):
    """
    Count all the hashtags in statuses
    """
    count = {}
    for item in statuses:
        if include_boosts and item["reblog"] is not None:
            item = item["reblog"]
        for name in [tag["name"] for tag in item["tags"]]:
            if name in count:
                count[name] += 1
            else:
                count[name] = 1
    return count

def print_tags(statuses, max, include_boosts):
    """
    Print hashtags used in statuses
    """
    if max == -1:
        print("All the hashtags:")
    else:
        print("Top " + str(max) + " hashtags:")
    count = tags(statuses, include_boosts)
    most = sorted(count.keys(), key = lambda tag: -count[tag])
    print(textwrap.fill(" ".join(
        ["#"+tag+"("+str(count[tag])+")" for tag in most[0:max]])))

def emoji(statuses):
    """
    Count all the emoji in statuses
    """
    count = {}
    for item in statuses:
        for char in item["content"]:
            if unicodedata.category(char) == 'So':
                if char in count:
                    count[char] += 1
                else:
                    count[char] = 1
    return count

def print_emoji(statuses, min = 10, max_num = 30):
    """
    Print emoji used in statuses, sorted by frequency
    """
    print("Most frequeny Emoji:")
    count = emoji(statuses)
    count = {k: v for k, v in count.items() if v >= min }
    most = sorted(count.keys(), key = lambda emoji: -count[emoji])
    print(textwrap.fill(" ".join([emoji for emoji in most[0:max_num]])))

def report(args):
    """
    Report on your toots and favourites
    """

    (username, domain) = args.user.split('@')

    status_file = domain + '.user.' + username + '.json'
    data = core.load(status_file, required=True, quiet=True, combine=args.combine)

    if args.all:
        print("Considering the entire archive")
        statuses = data["statuses"]
        favourites = data["favourites"]
    else:
        print("Considering the last "
              + str(args.weeks)
              + " weeks")
        statuses = core.keep(data["statuses"], args.weeks)
        favourites = core.keep(data["favourites"], args.weeks)

    if "statuses" in data:
        print("Statuses:".ljust(20), str(len(statuses)).rjust(6))
        print("Boosts:".ljust(20), str(boosts(statuses)).rjust(6))
        print("Media:".ljust(20), str(media(statuses)).rjust(6))

        print()
        print_tags(statuses, args.top, args.include_boosts)

        if args.with_emoji:
            print()
            print_emoji(statuses)

    if "statuses" in data and "favourites" in data:
        print()

    if "favourites" in data:
        print("Favourites:".ljust(20), str(len(favourites)).rjust(6))
        print("Boosts:".ljust(20), str(boosts(favourites)).rjust(6))
        print("Media:".ljust(20), str(media(favourites)).rjust(6))

        print()
        print_tags(favourites, args.top, args.include_boosts)
