import argparse
import json
import os

def create_cfn_generators_template(n):
    template = {
        'Description': 'Deploy several EC2 instances',
        'Parameters': {
            'KeyName': {
                'Description': 'Name of an existing EC2 KeyPair',
                'Type': 'String'
            },
            'Region': {
                'Description': 'AWS Region',
                'Type': 'String'
            }
        },
        'Mappings': {
            'RegionMap': {
                'us-east-1': {
                    'AMI': 'ami-047a51fa27710816e'
                },
                'us-west-1': {
                    'AMI': 'ami-005c06c6de69aee84'
                },
                'us-east-2': {
                    'AMI': 'ami-01aab85a5e4a5a0fe'
                },
                'us-west-2': {
                    'AMI': 'ami-0e999cbd62129e3b1'
                }
            }
        },
        'Outputs': {},
        'Resources': {
            'SSHSecurityGroup': {
                'Type': 'AWS::EC2::SecurityGroup',
                'Properties': {
                    'GroupDescription': 'Enable SSH Access',
                    'SecurityGroupIngress': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'FromPort': 22,
                            'IpProtocol': 'tcp',
                            'ToPort': 22
                        }
                    ]
                }
            }
        }
    }
    template_path = os.path.join(os.path.dirname(__file__), '..', 'DataGenerators.json')
    define_ec2_instances_and_outputs(template, n)
    with open(template_path, 'w') as f:
        json.dump(template, f)


def define_ec2_instances_and_outputs(template, n):
    for i in range(n):
        template['Resources'][f'EC2Instance{i}'] = {
            'Type': 'AWS::EC2::Instance',
            'Properties': {
                'KeyName': {
                    'Ref': 'KeyName'
                },
                'ImageId': {
                    'Fn::FindInMap': [
                        'RegionMap',
                        { 'Ref': 'Region' },
                        'AMI'
                    ]
                },
                'InstanceType': 't2.micro',
                'SecurityGroups': [
                    { 'Ref': 'SSHSecurityGroup' }
                ]
            }
        }

        template['Outputs'][f'PublicIP{i}'] = {
            'Value': {
                'Fn::GetAtt': [
                    f'EC2Instance{i}',
                    'PublicIp'
                ]
            },
            'Description': "Instance's public IP address"
        }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--NumberOfInstances', metavar='N', type=int, default=10, help='Number of Instances')
    args = parser.parse_args()
    create_cfn_generators_template(args.NumberOfInstances)