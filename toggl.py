import datetime

import re
import requests
from dateutil import parser, tz

TOGGLE_API_URL = 'https://www.toggl.com/api/v8/time_entries'
TOGGLE_AUTH = ('668ef91140905aa11b361b9c473967c0', 'api_token')
TOGGLE_ACTIVITY_TAGS = {'EDU': 38, 'SEO': 17, 'MEETING': 16, 'DOC': 15, 'STUDY': 14, 'PROJECT MANAGEMENT': 13,
                        'TEST': 12, 'BOOT STRAP': 11, 'NEED': 10, 'CODE': 9, 'DESIGN': 8}


class Toggle:
    def __init__(self, issue, duration, activity=TOGGLE_ACTIVITY_TAGS.get('CODE'), date=None, start=None, end=None,
                 description=None):
        self.issue = issue
        self.duration = duration
        self.activity = activity
        self.date = date
        self.start = start
        self.end = end
        self.description = description

    def __str__(self):
        return '#' + str(self.issue) + ' - ' + self.description

    @classmethod
    def create_toggles(cls, start_date=None, end_date=None):
        if not end_date:
            end_date = datetime.datetime.now(tz=tz.tzstr('UTC+03:30'))
        if not start_date:
            start_date = end_date - datetime.timedelta(days=30)

        response = requests.get(TOGGLE_API_URL,
                                params={'start_date': start_date.strftime('%Y-%m-%dT%H:%M:%S+03:30'),
                                        'end_date': end_date.strftime('%Y-%m-%dT%H:%M:%S+03:30')},
                                auth=TOGGLE_AUTH)

        times_json = response.json()
        entries = []
        for time in times_json:
            tags = time.get('tags')
            if tags:
                if 'PM' in tags:
                    continue
                elif 'No - PM' in tags:
                    print('Skipping entry (NO - PM):', time)
                    continue
                else:
                    activity = TOGGLE_ACTIVITY_TAGS.get('CODE')
                    if len(tags) == 1:
                        try:
                            activity = TOGGLE_ACTIVITY_TAGS.get(tags[0])
                        except KeyError:
                            print('Undefined tag', tags[0])
                            print('Skipping entry (' + tags[0] + '):', time)
                            continue
                    else:
                        print('More than one tag provided:', tags)
                        print('Skipping entry', tags, ':', time)
                        continue

            description = time.get('description')
            issue_description = re.search('#(?P<issue>\d+) *- *(?P<description>.*)', description)
            if issue_description:
                issue = issue_description.group('issue')
                description = issue_description.group('description')
            else:
                print('Skipping entry (ISSUE):', time)
                continue

            start = parser.parse(time.get('start'))
            date = start.date().strftime('%Y-%m-%d')
            start = start.time().strftime('%H:%M')

            end = parser.parse(time.get('stop'))
            end = end.time().strftime('%H:%M')

            duration = int(time.get('duration'))
            m, s = divmod(duration, 60)
            h, m = divmod(m, 60)
            duration = "%d:%02d" % (h, m)

            # noinspection PyUnboundLocalVariable
            entries.append(
                    Toggle(issue, duration, activity=activity, date=date, start=start, end=end,
                           description=description))

        return entries


items = Toggle.create_toggles()
print('--- FETCH DONE ---')
for i in items:
    print(str(i))
