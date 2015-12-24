# -*- coding: utf-8 -*-
import json

TEMPLATE = """
URL GOTO=http://pm.arsh.co/issues/{issue}/time_entries/new
TAG POS=1 TYPE=INPUT:TEXT FORM=ID:new_time_entry ATTR=ID:time_entry_spent_on CONTENT={date}
TAG POS=1 TYPE=INPUT:TEXT FORM=ID:new_time_entry ATTR=ID:time_entry_hours CONTENT={duration}
TAG POS=1 TYPE=INPUT:TEXT FORM=ID:new_time_entry ATTR=ID:time_entry_comments CONTENT={comment}
TAG POS=1 TYPE=SELECT FORM=ID:new_time_entry ATTR=ID:time_entry_activity_id CONTENT=%9
TAG POS=1 TYPE=INPUT:TEXT FORM=ID:new_time_entry ATTR=ID:time_entry_custom_field_values_1 CONTENT={start}
TAG POS=1 TYPE=INPUT:TEXT FORM=ID:new_time_entry ATTR=ID:time_entry_custom_field_values_2 CONTENT={end}
TAG POS=1 TYPE=SELECT FORM=ID:new_time_entry ATTR=ID:time_entry_custom_field_values_6 CONTENT=%0
TAG POS=1 TYPE=INPUT:SUBMIT FORM=ID:new_time_entry ATTR=NAME:commit

"""

times_file = open('times.toggl')
times_string = times_file.read()
times_file.close()
times_json = json.loads(times_string)

macro_file = open('times.iim', 'a')
for time in times_json:

    duration = time.get('duration')
    comment = time.get('message').replace(' ', '<SP>')

    macro = TEMPLATE.format(issue=time.get('issue'), date=time.get('date'), duration=duration, comment=comment,
                            start=time.get('start'), end=time.get('end'))
    macro_file.write(macro)

macro_file.close()
