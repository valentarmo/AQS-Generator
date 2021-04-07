import argparse
import boto3
import time
import sys
import os

from botocore.exceptions import ClientError


def deploy_stack(stack_name, key_name, region, private_key_s3_bucket, private_key_s3_path, client):
    if stack_exists(stack_name, client):
        update_stack(stack_name, key_name, region, client)
        wait_until_stack_is_updated(stack_name, client)
    else:
        create_stack(stack_name, key_name, region, client)
        wait_until_stack_is_created(stack_name, client)
    private_key_path = download_private_key(private_key_s3_bucket, private_key_s3_path, key_name) 
    create_hosts_file('Generators', private_key_path, get_hosts_ips(stack_name, client))


def stack_exists(stack_name, client):
    try:
        client.describe_stacks(StackName=stack_name)
        return True
    except ClientError:
        return False


def update_stack(stack_name, key_name, region, client):
    print('Updating CloudFormation Stack')
    dir_path = os.path.dirname(__file__)
    template_path = os.path.join(dir_path, '../', 'cloudformation/', 'DataGenerators.yaml')
    template_body = ''
    with open(template_path, 'r') as f:
        template_body = f.read()
    response = client.update_stack(
        StackName=stack_name,
        TemplateBody=template_body,
        Parameters=[
            {'ParameterKey': 'KeyName', 'ParameterValue': key_name},
            {'ParameterKey': 'Region', 'ParameterValue': region}
        ],
        Capabilities=['CAPABILITY_NAMED_IAM']
    )


def wait_until_stack_is_updated(stack_name, client):
    status = client.describe_stacks(StackName=stack_name)['Stacks'][0]['StackStatus']
    while status not in ['UPDATE_FAILED', 'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE']:
        time.sleep(5)
        status = client.describe_stacks(StackName=stack_name)['Stacks'][0]['StackStatus']
    if status == 'UPDATE_CREATE_FAILED' or status == 'UPDATE_ROLLBACK_COMPLETE':
        raise Exception('Stack Update Failed')
    print('Stack Updated')


def create_stack(stack_name, key_name, region, client):
    print('Creating CloudFormation Stack')
    dir_path = os.path.dirname(__file__)
    template_path = os.path.join(dir_path, '../', 'cloudformation/', 'DataGenerators.yaml')
    template_body = ''
    with open(template_path, 'r') as f:
        template_body = f.read()
    response = client.create_stack(
        StackName=stack_name,
        TemplateBody=template_body,
        Parameters=[
            {'ParameterKey': 'KeyName', 'ParameterValue': key_name},
            {'ParameterKey': 'Region', 'ParameterValue': region}
        ],
        Capabilities=['CAPABILITY_NAMED_IAM']
    )


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


def download_private_key(s3_bucket, key_path, key_name):
    print('Downloading Key Pair')
    s3 = boto3.client('s3')
    dir_path = os.path.dirname(__file__)
    file_name = os.path.join(dir_path, '..', key_name + '.pem')
    s3.download_file(s3_bucket, key_path, file_name)
    os.system(f'chmod 600 {file_name}')
    print(f'Key Pair Downloaded at {file_name}')
    return file_name


def create_hosts_file(group_name, private_key_path, hosts_ips):
    print('Creating hosts file')
    inventory_info =  f'[{group_name}]\n'
    for host_ip in hosts_ips:
        inventory_info += f'{host_ip}\n'
    inventory_info += f'\n[{group_name}:vars]\nansible_ssh_private_key_file={private_key_path}'
    dir_path = os.path.dirname(__file__)
    file_path = os.path.join(dir_path, '../', 'ansible/', 'hosts.ini')
    with open(file_path, 'w') as f:
        f.write(inventory_info)
    print(f'Hosts file created at {file_path}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--StackName', required=True, help='Name of the Stack')
    parser.add_argument('--KeyName', required=True, help='Name of the key pair to associate with the instances')
    parser.add_argument('--Region', help='Region where to create the Stack', default='us-east-2', choices=['us-west-1', 'us-east-1', 'us-west-2', 'us-east-2'])
    parser.add_argument('--PrivateKeyS3Bucket', required=True, help='S3 bucket with the .pem file')
    parser.add_argument('--PrivateKeyS3FilePath', required=True, help='Location of the .pem file in the s3 bucket')
    args = parser.parse_args()

    CloudFormation = boto3.client('cloudformation')
    try:
        deploy_stack(args.StackName, args.KeyName, args.Region, args.PrivateKeyS3Bucket, args.PrivateKeyS3FilePath, CloudFormation)
    except Exception as e:
        print(e)
        sys.exit(1)
