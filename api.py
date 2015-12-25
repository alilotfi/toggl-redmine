import copy


def fill_json(toggle, template):
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
