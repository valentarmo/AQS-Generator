#!/bin/python3

import argparse
import boto3
import yaml
import time
import os


def create_stack(stack_name, key_name, region, client):
    print('Creating CloudFormation Stack...')
    dir_path = os.path.dirname(__file__)
    template_path = os.path.join(dir_path, '../', 'cloudformation/', 'DataGenerators.yaml')
    template_body = ''
    with open(template_path, 'r') as f:
        template_body = f.read()
    response = CloudFormation.create_stack(
        StackName=args.StackName,
        TemplateBody=template_body,
        Parameters=[
            {'ParameterKey': 'KeyName', 'ParameterValue': key_name},
            {'ParameterKey': 'Region', 'ParameterValue': region}
        ],
        Capabilities=['CAPABILITY_NAMED_IAM']
    )
    return response['StackId']


def wait_until_stack_is_created(stack_name, client):
    status = client.describe_stacks(StackName=stack_name)['Stacks'][0]['StackStatus']
    while status not in ['CREATE_FAILED', 'CREATE_COMPLETE', 'ROLLBACK_COMPLETE']:
        time.sleep(5)
        status = client.describe_stacks(StackName=stack_name)['Stacks'][0]['StackStatus']
    if status == 'CREATE_FAILED' or status == 'ROLLBACK_COMPLETE':
        raise Exception('Stack Creation Failed')
    print('Stack created')


def get_hosts_ips(stack_name, client):
    response = client.describe_stacks(StackName=stack_name)
    return map(lambda output: output['OutputValue'],  response['Stacks'][0]['Outputs'])


def create_hosts_file(group_name, private_key_path, hosts_ips):
    inventory_info =  f'[{group_name}]\n'
    for host_ip in hosts_ips:
        inventory_info += f'{host_ip}\n'
    inventory_info += f'\n[{group_name}:vars]\nansible_ssh_private_key_file={private_key_path}'
    dir_path = os.path.dirname(__file__)
    file_path = os.path.join(dir_path, '../', 'ansible/', 'hosts.ini')
    with open(file_path, 'w') as f:
        f.write(inventory_info)


def create_taskcat_file(region):
    dir_path = os.path.dirname(__file__)
    taskcat_file_path = os.path.join(dir_path, '../', 'taskcat.yaml')
    contents = {
        'project': {
            'name': 'AQSDataGenerators',
            'regions': [region],
            'tests': {
                'creation-test': {
                    'template': 'cloudformation/DataGenerators.yaml'
                }
            }
        }
    }
    with open(taskcat_file_path, 'w') as f:
        yaml.dump(contents, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--StackName', required=True, help='Name of the Stack')
    parser.add_argument('--KeyName', required=True, help='Name of the key pair to associate with the instance')
    parser.add_argument('--Region', help='Region where to create the Stack', default='us-east-2', choices=['us-west-1', 'us-east-1', 'us-west-2', 'us-east-2'])
    parser.add_argument('--PrivateKeyFilePath', required=True, help='Location of the .pem file')
    args = parser.parse_args()

    CloudFormation = boto3.client('cloudformation')
    try:
        create_stack(args.StackName, args.KeyName, args.Region, CloudFormation)
        wait_until_stack_is_created(args.StackName, CloudFormation)
        create_hosts_file('Generators', args.PrivateKeyFilePath, get_hosts_ips(args.StackName, CloudFormation))
        create_taskcat_file(args.Region)
    except Exception as e:
        print(e)
