#!/usr/bin/env python3
# Copyright (C) 2018  Alex Schroeder <alex@gnu.org>
# Copyright (C) 2021  cutiful (https://github.com/cutiful)

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
import json
import http.server
import socketserver
from progress.bar import Bar
from urllib.parse import urlparse, parse_qs
from . import core

server_port = 13523
meow_origin = "https://purr.neocities.org"
meow_open_path = meow_origin + "/mastodon-archive-import/"

def meow(args):
    """
    Find and serve all archive files for Meow.
    """
    (username, domain) = args.user.split("@")

    status_file = domain + ".user." + username + ".json"
    data = core.load(status_file, required=True, quiet=True, combine=args.combine)

    media_dir = domain + ".user." + username
    media_files = []

    def use_local_file_if_exists(url):
        """
        Checks if we have the file, in which case returns the relative path, so
        that Meow knows to look it up in the local storage. Otherwise, returns
        the URL, so Meow will try to load it remotely. Adds relative paths to
        media_files to serve them to Meow.
        """

        nonlocal media_files

        path = urlparse(url).path
        if path in media_files:
            return path

        file_name = media_dir + path
        if os.path.isfile(file_name):
            media_files.append(path)
            return path
        else:
            return url

    transform_media_urls(data, use_local_file_if_exists)
    data["files"] = media_files

    print("Please, open Meow at", meow_open_path, "to continue!")

    file_cb = lambda *args: None

    bar = None
    if len(media_files) > 0:
        bar = Bar("Exporting files", max = len(media_files) + 1)
        file_cb = lambda *args: bar.next()

    serve(server_port, meow_origin, data, media_dir, media_files, file_cb)

    if bar:
        bar.finish()
    print("Export finished!")

def transform_media_urls(data, func):
    """
    Calls func on each media file URL and sets the latter to the result.
    """
    for collection in ["statuses", "favourites", "bookmarks"]:
        for status in data[collection]:
            attachments = status["media_attachments"]
            if status["reblog"] is not None:
                attachments = status["reblog"]["media_attachments"]
            for attachment in attachments:
                if attachment["url"]:
                    attachment["url"] = func(attachment["url"])

    for picture in ["avatar", "header"]:
        data["account"][picture] = func(data["account"][picture])

def serve(port, origin, data, media_dir, media_files, file_cb):
    complete = False
    def not_completed():
        nonlocal complete
        return not complete

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            nonlocal complete
            query = parse_qs(urlparse(self.path).query)

            if self.path == "/":
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", origin)
                self.send_header("Content-type", "application/json")
                self.end_headers()

                self.wfile.write(bytes(json.dumps(data), "utf-8"))

                file_cb()
            elif "file" in query and query["file"][0] in media_files:
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", origin)
                self.end_headers()

                file_name = media_dir + query["file"][0]
                with open(file_name, "rb") as file:
                    self.wfile.write(file.read())

                file_cb()
            elif "complete" in query:
                self.send_response(200)
                self.end_headers()

                complete = True
            else:
                self.send_error(404)

        def log_message(self, format, *args):
            return

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", port), Handler) as httpd:
        while not_completed():
            httpd.handle_request()
