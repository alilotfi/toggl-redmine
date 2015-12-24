import re
import requests
from dateutil import parser

ACTIVITY_CODE = 9


class Toggle:
    def __init__(self, issue, duration, activity=ACTIVITY_CODE, date=None, start=None, end=None, description=None):
        self.issue = issue
        self.duration = duration
        self.activity = activity
        self.date = date
        self.start = start
        self.end = end
        self.description = description

    @classmethod
    def create_toggles(cls):
        response = requests.get('https://www.toggl.com/api/v8/time_entries',
                                params={'start_date': '2015-11-14T00:00:00+03:30',
                                        'end_date': '2015-12-13T23:59:59+03:30'},
                                auth=('668ef91140905aa11b361b9c473967c0', 'api_token'))

        times_json = response.json()
        entries = []
        for time in times_json:
            if time.get('tags') and ('No - PM' in time.get('tags') or 'PM' in time.get('tags')):
                print('Skipping entry:', time)
                continue

            description = time.get('description')
            issue_description = re.search('#(?P<issue>\d+) *- *(?P<description>.*)', description)
            if issue_description:
                issue = issue_description.group('issue')
                description = issue_description.group('description')
            else:
                print('Skipping entry:', time)
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

            entries.append(Toggle(issue, duration, date=date, start=start, end=end, description=description))
