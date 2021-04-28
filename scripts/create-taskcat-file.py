import argparse
import yaml
import os

def create_taskcat_file(key_name, s3_bucket_name, region):
    dir_path = os.path.dirname(__file__)
    taskcat_file_path = os.path.join(dir_path, '../', '.taskcat.yml')
    contents = {
        'general': {
            'parameters': {
                'Region': region,
                'KeyName': key_name
            },
            's3_bucket': s3_bucket_name
        },
        'project': {
            'name': 'aqs-data-generators',
            'regions': [region],
        },
        'tests': {
            'creation-test': {
                'template': 'DataGenerators.json'
            }
        }
    }
    with open(taskcat_file_path, 'w') as f:
        yaml.dump(contents, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--KeyName', required=True, help='Name of the key pair to associate with the instances')
    parser.add_argument('--S3Bucket', required=True, help='Taskcat S3 Bucket')
    parser.add_argument('--Region', help='Region where to test the Stack', default='us-east-2', choices=['us-west-1', 'us-east-1', 'us-west-2', 'us-east-2'])
    args = parser.parse_args()

    try:
        create_taskcat_file(args.KeyName, args.S3Bucket, args.Region)
    except Exception as e:
        print(e)