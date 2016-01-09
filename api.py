import json
import sys

import copy
import requests
from config import get_redmine_key
from reporter import report, Color
from toggl import Toggle

JSON_TEMPLATE_PATH = 'entry_template.json'
API_URL = 'http://pm.arsh.co/time_entries.xml'

JSON_HEADERS = {'Content-type': 'application/json',
                'X-Redmine-API-Key': get_redmine_key()}
LOCATIONS = {'office': 'شرکت', 'remote': 'دورکاری'}


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
    if toggle.remote:
        fields[2]['value'] = LOCATIONS.get('remote')
        fields[3]['value'] = 1
    else:
        fields[2]['value'] = LOCATIONS.get('office')
        fields[3]['value'] = 0
    return template


def submit_entries(start_date=None, end_date=None):
    json_template = open(JSON_TEMPLATE_PATH)
    json_template = json.loads(json_template.read())

    report('Fetching time entries from toggl.com', Color.INFO)
    toggles = Toggle.create_toggles(start_date, end_date)
    report('Submitting' + str(len(toggles)) + 'entries to Arsh pm.', Color.INFO)
    for toggle in toggles:
        report(str(toggle), Color.HEADER, ' ')
        report('- Preparing...', end=' ')
        data = render_json(toggle, json_template)
        response = requests.post(API_URL, data=json.dumps(data), headers=JSON_HEADERS)
        if not response.status_code == 201:
            report('Submission failed. Reason: %s' % response.reason, Color.FAILURE)
            continue

        report('Submitted', Color.SUCCESS, ' ')
        toggle.add_tag()
        report('Tagged.', Color.SUCCESS)


start = None
end = None
if len(sys.argv) == 2:
    end = sys.argv[1]
if len(sys.argv) == 3:
    start = sys.argv[1]
    end = sys.argv[2]
submit_entries(start, end)
