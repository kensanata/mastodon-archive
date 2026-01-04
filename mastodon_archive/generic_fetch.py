#!/usr/bin/env python3
# Copyright (C) 2026       Jonathan Kamens <jik@kamens.us>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

from . import core

import datetime
import json
import sys


def custom_json(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError(f'Cannot serialize object of {type(obj)}')


def generic_fetch(args, method, plaintext_formatter, paginatable=True):
    mastodon = core.readwrite(args)
    items = getattr(mastodon, method)()
    if paginatable:
        items = mastodon.fetch_remaining(first_page=items)
    if args.json:
        json.dump(items, sys.stdout, indent=2, default=custom_json)
    else:
        for item in items:
            print(plaintext_formatter(item))


def followed_tags(args):
    generic_fetch(args, 'followed_tags',
                  lambda tag: f'#{tag.name}')


def filters(args):
    generic_fetch(
        args, 'filters_v2',
        lambda filter: f'title={filter.title} '
        f'keywords={",".join(k.keyword for k in filter["keywords"])}',
        paginatable=False)
