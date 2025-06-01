import os
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8080")
WORKER_TOKEN = os.getenv("AUTH_TOKEN")
PUBLIC_IP = os.getenv("PUBLIC_IP")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-2")
METAPILOT_TOKEN = os.getenv("METAPILOT_TOKEN")

BACKUP_BUCKET = os.getenv("BACKUP_BUCKET", "collate-saas-provisioner-us-east-2")

#DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
DRY_RUN = False

default_tags = {'provisioner': 'saas-creator', 'owner': 'devops'}
alarms_sns = f'arn:aws:sns:{AWS_DEFAULT_REGION}:118146679784:sns-admin-prod'

ip_ranges = {
    'eu-west-1': '10.85.128.0/18', # Ireland
    'eu-west-3': '10.84.0.0/18', # Paris
    'eu-central-1': '10.84.64.0/18', # Frankfurt
    'us-east-1': '10.84.128.0/18', # N Virginia
    'us-west-1': '10.84.192.0/18', # N California
    'ap-southeast-2': '10.85.0.0/18', # Sydney
    'ap-northeast-1': '10.85.64.0/18', # Tokyo
    'ap-south-1': '10.85.192.0/18', # Mumbai
}

available_regions = {
    'eu-west-1': 'Ireland',
    'eu-west-3': 'Paris',
    'eu-central-1': 'Frankfurt',
    'us-east-1': 'N Virginia',
    'us-west-1': 'N California',
    'ap-southeast-2': 'Sydney',
    'ap-northeast-1': 'Tokyo',
    'ap-south-1': 'Mumbai',
}