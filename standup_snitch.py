#! /usr/bin/env python3

# Using the Slack API:
# (1) Get recent history (midnight last night back to a specified
#     number of days before that) of a specified input channel.
# (2) Count how many of those days each user made a post in the channel.
# (3) Post a report to a specified output channel, calling out the
#     inactive users.
#
# Usage: python3 standup_snitch.py -t api_token.txt \
#                                  -d 14 \
#                                  -i input_channel.csv \
#                                  -o output_channel.csv \
#                                  -u users.csv \
#                                  -b SnitchBot

import urllib.request
import urllib.parse
import json
import time
import datetime
import csv
import argparse

def format_channel(channel_dict):
    return ''.join(['<#',
                    channel_dict['channel_id'],
                    '|',
                    channel_dict['channel_name'],
                    '>'])

def format_user(user_dict):
    return ''.join(['<@',
                    user_dict['user_id'],
                    '|',
                    user_dict['user_name'],
                    '>'])

def get_message_history(token, channel, ts_start, ts_end):
    # 1000 messages is the maximum allowed by the API.
    arguments = urllib.parse.urlencode({'token': token,
                                        'channel': channel,
                                        'latest': ts_end,
                                        'oldest': ts_start,
                                        'count': 1000}).encode()
    response = urllib.request.urlopen('https://slack.com/api/channels.history',
                                      data = arguments)

    history_raw = json.loads(response.read().decode())
    history_processed = []

    if history_raw['ok']:
        for message in history_raw['messages']:
            if message['type'] == 'message':
                history_processed.append({'user': message['user'],
                                          'ts': message['ts']})
    else:
        raise Exception('Slack API returned error', history_raw['error'])

    return history_processed

def histogram_user_activity(history, users, ts_start, duration_in_days):
    user_activity_dict = {}
    for user_dict in users:
        user_activity_dict[user_dict['user_id']] \
            = [False for _ in range(duration_in_days)]

    for message in history:
        try:
            day = int((float(message['ts']) - ts_start) / (3600 * 24))
            user_activity_dict[message['user']][day] = True
        except KeyError:
            # Post from someone we're not tracking
            pass

    user_activity_hist = {u: sum(user_activity_dict[u])
                          for u in user_activity_dict}

    return user_activity_hist

def post_message(token, channel, text, bot_name):
    arguments = urllib.parse.urlencode({'token': token,
                                        'channel': channel,
                                        'text': text,
                                        'username': bot_name}).encode()
    response = urllib.request.urlopen('https://slack.com/api/chat.postMessage',
                                      data = arguments)

    result = json.loads(response.read().decode())

    if result['ok']:
        return
    else:
        raise Exception('Slack API returned error', result['error'])

# Command line flags
parser = argparse.ArgumentParser()
parser.add_argument('-t', '--token_file', help = 'file with API token')
parser.add_argument('-d', '--duration', type = int,
                    help = 'duration to check in days')
parser.add_argument('-i', '--input_channel_file',
                    help = 'file with Slack channel to monitor')
parser.add_argument('-o', '--output_channel_file',
                    help = 'file with Slack channel to write to')
parser.add_argument('-u', '--user_file', help = 'file with user list')
parser.add_argument('-b', '--bot_name', help = 'display name of bot')
args = parser.parse_args()

duration_in_days = args.duration
bot_name = args.bot_name

# Read configuration from the specified files
with open(args.token_file) as token_file:
    token = token_file.read().strip()

with open(args.input_channel_file) as input_channel_file:
    # Take only the first line after the header
    input_channel = next(csv.DictReader(input_channel_file))

with open(args.output_channel_file) as output_channel_file:
    # Take only the first line after the header
    output_channel = next(csv.DictReader(output_channel_file))

with open(args.user_file) as user_file:
    users = [user for user in csv.DictReader(user_file)]

# Calculate the timestamp start of measurement time, based on a 24-hour day and
# based on accurate time on the host computer. Assumes no Daylight
# Savings boundaries in the period of interest. Be warned!
ts_now = time.time()
now = datetime.datetime.now()
last_night_midnight = datetime.datetime(now.year, now.month, now.day)
ts_end = int(ts_now - (now - last_night_midnight).total_seconds())
ts_start = ts_end - duration_in_days * 24 * 3600

# Slack API call to get history
message_history = get_message_history(token,
                                      input_channel['channel_id'],
                                      ts_start,
                                      ts_end)

# Histogram messages, chunking by day
message_histogram = histogram_user_activity(message_history,
                                            users,
                                            ts_start,
                                            duration_in_days)

print(message_histogram)

# Sort by message count; build text histogram; list the non-participants
print("On how many of the last", duration_in_days,
      "days did you check in on", format_channel(input_channel) + "?",
      "\n")

print('```')
print('```')

print(', '.join(map(format_user, users)) + ', we miss you.')

# Slack API call to publish summary
# post_message(token, output_channel['channel_id'], summary_text, bot_name)
