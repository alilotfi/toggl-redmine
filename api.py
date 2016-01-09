import json
import sys

import copy
import requests
from toggl import Toggle

JSON_TEMPLATE_PATH = 'entry_template.json'
API_URL = 'http://pm.arsh.co/time_entries.xml'
JSON_HEADERS = {'Content-type': 'application/json',
                'X-Redmine-API-Key': '71552af7e0259ea8e939f0704065ec09c6587776'}


def render_json(toggle, template):
    template = copy.deepcopy(template)
    entry = template.get('time_entry')
    entry['issue_id'] = toggle.issue
    entry['activity_id'] = toggle.activity
    entry['hours'] = toggle.duration
    entry['comments'] = toggle.description
    entry['spent_on'] = toggle.date
    fields = entry.get('custom_fields')
    fields[0]['value'] = toggle.start
    fields[1]['value'] = toggle.end
    return template


def report(status, color=None, end_line=False):
    string = '%s'
    if color == 'green':
        string = '\033[92m' + string + '\033[0'
    elif color == 'red':
        string = '\033[91m' + string + '\033[0'
    elif color == 'blue':
        string = '\033[94m' + string + '\033[0'

    if end_line:
        string += '\n'

    sys.stdout.write(string % status)
    sys.stdout.flush()


def submit_entries(start_date=None, end_date=None):
    json_template = open(JSON_TEMPLATE_PATH)
    json_template = json.loads(json_template.read())

    report('Fetching time entries from toggl.com', 'blue', True)
    toggles = Toggle.create_toggles(start_date, end_date)
    report('Submitting' + str(len(toggles)) + 'entries to Arsh pm.', 'blue', True)
    for toggle in toggles:
        report(str(toggle) + ' - ')
        report('Preparing for submit. ')
        data = render_json(toggle, json_template)
        response = requests.post(API_URL, data=json.dumps(data), headers=JSON_HEADERS)
        if not response.status_code == 201:
            report('Submission failed. Reason: %s' % response.reason, 'red', True)
            sys.stdout.flush()
            continue

        report('Submission succeeded. ', 'green')
        toggle.add_tag()
        report('Tagged.', 'green', True)


start = None
end = None
if len(sys.argv) == 2:
    end = sys.argv[1]
if len(sys.argv) == 3:
    start = sys.argv[1]
    end = sys.argv[2]
submit_entries(start, end)
