import json
import os

DOC_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'documents')

EMAIL_TEMPLATE_PATH = os.path.join(DOC_PATH, 'email_templates.json')
JOB_PROPERTIES_PATH = os.path.join(DOC_PATH, 'job_properties.json')

def read_email_templates():
    with open(EMAIL_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_email_templates(data):
    with open(EMAIL_TEMPLATE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def read_job_properties():
    with open(JOB_PROPERTIES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_job_properties(data):
    with open(JOB_PROPERTIES_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2) 