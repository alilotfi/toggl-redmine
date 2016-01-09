import datetime
import json

import re
import requests
from dateutil import parser, tz
from reporter import report, Color

TOGGLE_API_URL = 'https://www.toggl.com/api/v8/time_entries'
TOGGLE_AUTH = ('668ef91140905aa11b361b9c473967c0', 'api_token')
TOGGLE_ACTIVITY_TAGS = {'EDU': 38, 'SEO': 17, 'MEETING': 16, 'DOC': 15, 'STUDY': 14, 'PROJECT MANAGEMENT': 13,
                        'TEST': 12, 'BOOT STRAP': 11, 'NEED': 10, 'CODE': 9, 'DESIGN': 8}
TOGGLE_REMOTE_TAG = 'Remote'


class Toggle:
    def __init__(self, entry_id, issue, duration, activity=TOGGLE_ACTIVITY_TAGS.get('CODE'), date=None, start=None,
                 end=None, description=None, remote=False):
        self.entry_id = entry_id
        self.issue = issue
        self.duration = duration
        self.activity = activity
        self.date = date
        self.start = start
        self.end = end
        self.description = description
        self.remote = remote

    def __str__(self):
        return str(self.entry_id) + ' #' + str(self.issue) + ' - ' + self.description

    @classmethod
    def get_entry(cls, entry_id):
        return requests.get(TOGGLE_API_URL + '/' + str(entry_id), auth=TOGGLE_AUTH)

    def add_tag(self, tag='PM'):
        response = Toggle.get_entry(self.entry_id)
        entry = response.json()
        tags = entry.get('data').get('tags', [])
        if tag in tags:
            return False

        tags.append(tag)
        request = {'time_entry': {'tags': tags}}
        request = json.dumps(request)
        t_response = requests.put(TOGGLE_API_URL + '/' + str(self.entry_id), data=request, auth=TOGGLE_AUTH)
        return t_response.status_code == 200

    @classmethod
    def create_toggles(cls, start_date=None, end_date=None):
        if not end_date:
            end_date = datetime.datetime.now(tz=tz.tzstr('UTC+03:30'))
        if not start_date:
            start_date = end_date - datetime.timedelta(days=30)

        if start_date is str:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        if end_date is str:
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

        response = requests.get(TOGGLE_API_URL,
                                params={'start_date': start_date.strftime('%Y-%m-%dT%H:%M:%S+03:30'),
                                        'end_date': end_date.strftime('%Y-%m-%dT%H:%M:%S+03:30')},
                                auth=TOGGLE_AUTH)

        times_json = response.json()
        entries = []
        for time in times_json:
            entry_id = time.get('id')
            description = time.get('description')
            activity = TOGGLE_ACTIVITY_TAGS.get('CODE')
            tags = time.get('tags')

            if tags:
                if 'PM' in tags:
                    continue
                elif 'No - PM' in tags:
                    report('Skipping entry (NO - PM):' + entry_id + description, Color.WARNING)
                    continue

                remote = False
                if TOGGLE_REMOTE_TAG in tags:
                    remote = True
                    tags.remove(TOGGLE_REMOTE_TAG)

                if len(tags) > 1:
                    report('More than one tag provided: ' + tags, Color.WARNING)
                    report('Skipping entry ' + tags + ':' + entry_id + ' ' + description, Color.WARNING)
                    continue
                elif len(tags) == 1:
                    activity = TOGGLE_ACTIVITY_TAGS.get(tags[0])
                    if not activity:
                        report('Undefined tag ' + tags[0], Color.WARNING)
                        report('Skipping entry (' + tags[0] + '): ' + entry_id + ' ' + description, Color.WARNING)
                        continue

            issue_description = re.search('#(?P<issue>\d+) *- *(?P<description>.*)', description)
            if issue_description:
                issue = issue_description.group('issue')
                description = issue_description.group('description')
            else:
                report('Skipping entry (ISSUE): ' + entry_id + ' ' + description, Color.WARNING)
                continue

            start = parser.parse(time.get('start')).astimezone(tz=tz.tzstr('UTC+03:30'))
            date = start.date().strftime('%Y-%m-%d')
            start = start.time().strftime('%H:%M')

            end = parser.parse(time.get('stop')).astimezone(tz=tz.tzstr('UTC+03:30'))  # TODO: Breaks on running entry
            end = end.time().strftime('%H:%M')

            duration = int(time.get('duration'))
            m, s = divmod(duration, 60)
            h, m = divmod(m, 60)
            duration = "%d:%02d" % (h, m)

            entries.append(
                    Toggle(entry_id, issue, duration, activity=activity, date=date, start=start, end=end,
                           description=description, remote=remote))

        return entries
