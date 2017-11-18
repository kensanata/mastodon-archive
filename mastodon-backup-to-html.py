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
import json
import html2text
import datetime
import dateutil.parser

argv = sys.argv

if len(argv) != 2:
    print("Usage: %s username@instance" % argv[0])
    sys.exit(1)

(username, domain) = argv[1].split('@')

status_file = domain + '.user.' + username + '.json'

if not os.path.isfile(status_file):

    print("You need to run mastodon-backup.py, first")
    sys.exit(2)

with open(status_file, mode = 'r', encoding = 'utf-8') as fp:
    data = json.load(fp)

user = data["account"]
statuses = data["statuses"]
    
header_template = '''\
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>%s</title>
<style type="text/css">
body {
        font-family: sans-serif;
        background: #191B22;
        font-size: 14px;
        line-height: 18px;
        font-weight: 400;
        color: #fff;
        text-rendering: optimizelegibility;
        -webkit-font-feature-settings: "kern";
        font-feature-settings: "kern";
        -webkit-text-size-adjust: none;
        -moz-text-size-adjust: none;
        -ms-text-size-adjust: none;
        text-size-adjust: none;
        -webkit-tap-highlight-color: transparent;
        max-width: 80ex;
}
.column {
	background: #282c37;
        padding: 10px;
        margin: 10px;
}
h1 {
	color: #fff;
	font-size: 20px;
	line-height: 27px;
	font-weight: 500;
	overflow: hidden;
	text-overflow: ellipsis;
        text-align: center;
}
.account {
        text-align: center;
}
.account .nick {
	color: #2b90d9;
	margin-bottom: 10px;
}
.account .bio, .bio a, .bio a:visited {
	color: #d9e1e8;
}
.meta {
	color: #606984;
	font-size: 15px;
}
.meta strong {
        font-weight: 500;
}
a {
        text-decoration: none;
}
a:hover {
        text-decoration: underline;
}
.wrapper {
	padding-top: 10px;
	border-top: 1px solid #393f4f;
}
.boosted a {
	color: #606984;
}
.boosted a:visited {
	color: #606984;
}
.boosted {
	padding-bottom: 10px;
}
.meta a {
	color: #fff;
}
.meta a:visited {
	color: #fff;
}
.meta .time {
	display: block;
	float: right;
}
.content a {
	color: #d9e1e8;
	
}
.content a:visited {
	color: #d9e1e8;
	
}
</style>
</head>
<body>
<div class="column">
<h1 class="name">%s</h1>
<div class="account">
<p class="nick">@%s</p>
<div class="bio">
%s
</div>
</div>
'''

footer_template = '''\
</div>
</body>
</html>\
'''

boost_template = '''\
<div class="boosted">
<a class="name" href="%s">%s</a> boosted
</div>
'''

status_template = '''\
<div class="status">
<div class="meta">
<strong class="name"><a href="%s">%s</a></strong>
<span class="nick">@%s</span>
<span class="time">%s</span>
</div>
<div class="content">
%s
</div>
</div>
'''

wrapper_template = '''\
<div class="wrapper">
%s%s
</div>
'''

if len(statuses) > 0:

    print(header_template % (
        user["display_name"],
        user["display_name"],
        user["username"],
        user["note"]))
    
    for status in statuses:
        
        boost = "";
        if status["reblog"] is not None:
            user = status["account"]
            boost = boost_template % (
                user["url"],
                user["display_name"])
            # display the boosted status instead
            status = status["reblog"]
            
        user = status["account"]
        info = status_template % (
            user["url"],
            user["display_name"],
            user["username"],
            dateutil.parser.parse(
                status["created_at"]).strftime(
                    "%Y-%m-%d %H:%M"),
            status["content"])

        html = wrapper_template % (boost, info)
        print(html)

    print(footer_template)
