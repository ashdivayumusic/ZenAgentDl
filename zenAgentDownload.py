import os
import csv
from datetime import datetime
import xml.etree.ElementTree as ET

def load_instances_from_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    instances = []
    for instance in root.findall('instance'):
        subdomain = instance.find('subdomain').text
        email = instance.find('email').text
        token = instance.find('token').text
        instances.append({'subdomain': subdomain, 'email': email, 'token': token})
    return instances

def compile_agents_into_csv(instances):
    if not instances:
        print("No instances loaded.")
        return

    fieldnames = ['Subdomain', 'Email', 'Token', 'DateChecked']
    today_date = datetime.now().strftime("%Y-%m-%d")

    with open('instances.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for instance in instances:
            row = {
                'Subdomain': instance['subdomain'],
                'Email': instance['email'],
                'Token': instance['token'],
                'DateChecked': today_date
            }
            writer.writerow(row)

if __name__ == "__main__":
    zendesk_instances = load_instances_from_xml('instances.xml')
    if zendesk_instances:
        compile_agents_into_csv(zendesk_instances)
    else:
        print("Failed to load instances from XML. Please check the XML file.")
