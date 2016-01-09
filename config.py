import json

config_file = open('api.conf')
config_json = json.loads(config_file.read())


def get_redmine_key():
    return config_json.get('redmine_key')


def get_toggl_key():
    return config_json.get('toggl_key')
