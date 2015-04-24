#! /usr/bin/env python3

import urllib.request
import urllib.parse
import json

class SlackAPIError(Exception):
    def __init__(self, message):
        super().__init__(message)

def call_slack(command, arg_dict):
    arguments = urllib.parse.urlencode(arg_dict).encode()

    response = urllib.request.urlopen('https://slack.com/api/' + command,
                                      data = arguments)

    results = json.loads(response.read().decode())

    if results['ok']:
        return results
    else:
        raise SlackApiError(results['error'])
