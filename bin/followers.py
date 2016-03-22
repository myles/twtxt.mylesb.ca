import re

import click

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

twtxt_pattern = re.compile(r'(?P<agent>\S+) \(\+(?P<url>\S+); @(?P<username>\S+)\)')

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

    return [dict(tupleized) for tupleized in set(tuple(item.items()) for item in followers)]


@click.command()
@click.argument('access_log_file')
def main(access_log_file):
    access_log = get_access_log(access_log_file)
    followers = get_twtxt_followers(access_log)
    output = []

    for follower in followers:
        output.append('@%(username)s - %(url)s' % follower)

    click.echo_via_pager('\n'.join(set(output)))


if __name__ == "__main__":
    main()
