#!/usr/bin/env python
"""
iCal to json
============

By Remigiusz 'lRem' Modrzejewski.

This script is created to automatically update the WordPress page
of the *weekly* seminars of COATI team.
You're free to adapt it to your needs,
but it would be nice if you kept a link to my website in your page ;)

License Info
------------

Copyright (c) 2013, Remigiusz 'lRem' Modrzejewski
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
      * Neither the name of INRIA, I3S, CNRS, UNS, PACA nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL Remigiusz Modrzejewski BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import requests
import json
import re

from parse import parse_calendar


def get_args():
    """
    Parses command line arguments.
    :return: an `argparse.namespace` object with the runtime arguments
    """
    import argparse
    parser = argparse.ArgumentParser()
    add = parser.add_argument
    add('url', help='url of the ics file')
    add('out', help='the output JSON file path')
    return parser.parse_args()


def get_ics(url):
    """
    Gets the ICS file residing at the given url.
    :param url: the url from which to download the ics file
    :type url: str
    :return: string containing the ical file contents
    """
    req = requests.get(url)
    assert req.ok, "Failed to download the file"
    return req.text


def dump_json(data, fname):
    """
    Save the data in a file in JSON format.
    :param data: data to save
    :type data: anything accepted by `json.dump`
    :param fname: file name (including path) to save at
    :type fname: str
    """
    out = open(fname, 'w')
    json.dump(data, out)


def add_formatting(data):
    """
    Add a little bit of formatting.
    Modifies `data` in-place.
    :param data: list of event dictionaries
    :type data: as returned by `parse.parse_calendar`
    """
    for event in data:
        event['ABSTRACT'] = re.sub('\n\s*\n', '</p><p>', event['ABSTRACT'])


def main():
    args = get_args()
    ics = get_ics(args.url)
    parsed = parse_calendar(ics)
    parsed.sort(key=lambda e: e['EPOCH'], reverse=True)
    add_formatting(parsed)
    dump_json(parsed, args.out)

if __name__ == '__main__':
    main()
