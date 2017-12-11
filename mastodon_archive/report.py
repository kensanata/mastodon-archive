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
from . import core

def boosts(list):
    """
    Count boosts in a list of statuses
    """
    i = 0
    for item in list:
        if item["reblog"] is not None:
            i += 1
    return i

def media(list):
    """
    Count media attachments in a list of statuses
    """
    i = 0
    for item in list:
        i += len(item["media_attachments"])
    return i


def tags(list):
    """
    Count all the hashtags in a list of statuses
    """
    count = {}
    for item in list:
        for name in [tag["name"] for tag in item["tags"]]:
            if name in count:
                count[name] += 1
            else:
                count[name] = 1
    return count

def print_tags(list, max=10):
    """
    Count media attachments in a list of statuses
    """
    count = tags(list)
    most = sorted(count.keys(), key = lambda tag: -count[tag])
    for tag in most[0:max]:
        print(("#" + tag + ":").ljust(20), str(count[tag]).rjust(6))

def report(args):
    """
    Report on your toots and favourites
    """

    (username, domain) = args.user.split('@')

    status_file = domain + '.user.' + username + '.json'
    data = core.load(status_file, required = True, quiet = True)

    if "statuses" in data:
        print("Statuses:".ljust(20), str(len(data["statuses"])).rjust(6))
        print("Boosts:".ljust(20), str(boosts(data["statuses"])).rjust(6))
        print("Media:".ljust(20), str(media(data["statuses"])).rjust(6))
        
    if "favourites" in data:
        print("Favourites:".ljust(20), str(len(data["favourites"])).rjust(6))

    print()
    print_tags(data["statuses"])
