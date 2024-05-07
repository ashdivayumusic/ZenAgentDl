import requests
import csv
from datetime import datetime, timedelta
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

def get_agents(instance):
    url = f"https://{instance['subdomain']}.zendesk.com/api/v2/users.json?role[]=agent&role[]=admin"
    auth = (f"{instance['email']}/token", instance['token'])
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        return response.json()['users']
    else:
        print(f"Failed to fetch agents from {instance['subdomain']}. Status code: {response.status_code}")
        return []

def days_since_last_login(last_login):
    if last_login:
        last_login_date = datetime.strptime(last_login, '%Y-%m-%dT%H:%M:%SZ')
        delta = datetime.now() - last_login_date
        if delta < timedelta(days=1):
            return '0'
        return delta.days
    return 'N/A'

def compile_agents_into_csv(instances):
    if not instances:
        print("No instances loaded.")
        return

    fieldnames = ['Name', 'Email', 'LastLogin', 'DaysSinceLastLogin', 'UserType', 'RoleType'] + [inst['subdomain'] for inst in instances]

    with open('agents.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for instance in instances:
            agents = get_agents(instance)
            for agent in agents:
                if agent['role_type'] != 1:
                    row = {
                        'Name': agent['name'],
                        'Email': agent['email'],
                        'LastLogin': agent['last_login_at'],
                        'DaysSinceLastLogin': days_since_last_login(agent['last_login_at']),
                        'UserType': agent['role'],
                        'RoleType': agent['role_type']
                    }
                    for inst in instances:
                        row[inst['subdomain']] = ''
                    row[instance['subdomain']] = 'X'
                    writer.writerow(row)

if __name__ == "__main__":
    zendesk_instances = load_instances_from_xml('instances.xml')
    if zendesk_instances:
        compile_agents_into_csv(zendesk_instances)
    else:
        print("Failed to load instances from XML. Please check the XML file.")
