#!/usr/bin/env python3
"""
Extract your TwTxt followers from an Apache or Nginx access.log.

Copyright (c) 2016, Myles Braithwaite <me@mylesbraithwaite.com>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

* Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in
  the documentation and/or other materials provided with the
  distribution.

* Neither the name of the Myles Braithwaite nor the names of its
  contributors may be used to endorse or promote products derived
  from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY
WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

import re

import click

from twtxt.config import Config

log_parts = [
    r'(?P<host>\S+)',       # host %h
    r'\S+',                 # indent %l (unused)
    r'(?P<user>\S+)',       # user %u
    r'\[(?P<time>.+)\]',    # time %t
    r'"(?P<request>.+)"',   # request "%r"
    r'(?P<status>[0-9]+)',  # status %>s
    r'(?P<size>\S+)',       # size %b (careful, can be '-')
    r'"(?P<referer>.*)"',   # referer "%{Referer}i"
    r'"(?P<agent>.*)"',     # user agent "%{User-agent}i"
]

log_pattern = re.compile(r'\s+'.join(log_parts)+r'\s*\Z')

twtxt_pattern = re.compile(r'(?P<agent>\S+) \(\+(?P<url>\S+); '
                           '@(?P<username>\S+)\)')


def get_access_log(access_log_filename):
    lines = []

    with open(access_log_filename, 'r') as f:
        for line in f:
            match = log_pattern.match(line)
            lines.append(match.groupdict())

    return lines


def get_twtxt_followers(access_log):
    followers = []

    for entry in access_log:
        agent = entry['agent']

        match = twtxt_pattern.match(agent)

        if match:
            followers.append(match.groupdict())

    return [dict(tupleized) for tupleized in set(tuple(item.items())
            for item in followers)]


def check_if_following(follower):
    config = Config.discover()

    if config.get_source_by_nick(follower):
        return True

    return False


@click.command()
@click.argument('access_log_file')
def main(access_log_file):
    access_log = get_access_log(access_log_file)
    followers = get_twtxt_followers(access_log)
    out = []

    for follower in followers:
        if check_if_following(follower['username']):
            out.append(click.style('✓ @{username} - {url}'.format(**follower),
                                   fg='green'))
        else:
            out.append(click.style('✗ @{username} - {url}'.format(**follower),
                                   fg='red'))

    click.echo_via_pager('\n'.join(set(out)))


if __name__ == "__main__":
    main()
