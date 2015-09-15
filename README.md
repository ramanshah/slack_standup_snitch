# Slack Standup Snitch

![snitch_bot_in_action](https://cloud.githubusercontent.com/assets/8029092/7402900/f85095c0-ee95-11e4-91e7-940717732f3b.jpg)

The Slack Standup Snitch is a [Slack](https://slack.com/) bot that
counts the unique days that each user was active on a specified
channel and calls out the inactive users. It runs on Python 3 without
any further dependencies. It does the timestamp math to grab the posts
from Slack between midnight the previous night and n days before
that. It aggregates the *unique* days - if you posted five times on
Monday and once on Wednesday, that counts for two days. It returns a
text histogram of the activity and "ats" the users who checked in zero
times.

## Setup instructions

1. Clone this repo.
2. [Get a Slack API token.](https://api.slack.com/web) Save it to the
   repo's directory under `api_token.txt`. (You can save it wherever
   you want, but the `.gitignore` is put together to make this a
   convenient choice. The same is true for the other filenames below.)
3. Get a list of your users along with their internal Slack IDs:

   ```
   python3 list_users.py < api_token.txt > users.csv
   ```

   Typically you'll manually edit `users.csv` to pare the list down to
   the active people you want to monitor.
4. Get a list of your channels along with their internal Slack IDs:

   ```
   python3 list_channels.py < api_token.txt > input_channel.csv
   cp input_channel.csv output_channel.csv
   ```

   Manually remove all but two lines from each file:
   `input_channel.csv` should have a header and the line for the
   channel you want to monitor. Similarly, `output_channel.csv` should
   have a header and the line for the channel you want to send the
   report to.

## How to use

### Typical use

I run the bot from my work computer each Monday morning:
```
python3 standup_snitch.py -t api_token.txt \
                          -d 7 \
                          -i input_channel.csv \
                          -o output_channel.csv \
                          -u users.csv \
                          -b SnitchBot
```
Configure as you see fit; name the bot creatively; put it in a
crontab; and take good care of your people!

### Other features

* `-r`: Dry-run the `standup_snitch` report to standard output instead
of sending it to Slack.

### Maintaining the user list

You can manually maintain `users.csv` to add users (running
`list_users.py` and merging the lists) and remove users (deleting
lines from `users.csv`). However, since internships, vacations, and
normal turnover means that the set of active users changes frequently,
two `bash` scripts are included to make these tasks easier. Each
script creates a file `users.csv.new`, shows you the proposed changes,
and prompts you to verify the changes before applying them.

* `bash add_user.sh users.csv new_user_name api_token.txt`
* `bash remove_user.sh users.csv user_to_remove`

## Philosophy

I am releasing this with trepidation because I know it's going to be
used by lousy bosses to harass their workers. In
[our academic research group](http://stephenslab.uchicago.edu), we use
Slack, which we've found to be a great way to organize communications
between a bunch of busy people with varied schedules and semi-remote
working habits. (Much better than endless email threads with
ever-changing cc lists.) One of the ongoing expectations in our lab is
to touch base at least weekly on a `#standup` Slack channel to let
your peers know what you've worked on, what you plan to work on, and
if you're stuck on anything.

I've personally seen a lot of very talented people drop out of
Ph.D. programs. In my experience, graduation rate has seemed highly
correlated with engaging one's peers about one's challenges in the
process of overcoming them. (Notably, it has also seemed almost
uncorrelated with intelligence; virtually everyone who gets into a
graduate program is smart enough to graduate.) Dropping out of grad
school seems to me to be mostly a failure of community. For this
reason, I was pleased to see the `#standup` channel when I started
here and felt motivated to help enforce its usage. I wrote this bot to
automate the process of following up on students who might fall
through the cracks without extra attention.
