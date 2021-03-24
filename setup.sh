#!/bin/bash

StackName=""
KeyName=""
PrivateKeyFilePath=""
AwsAccessKeyId=""
AwsSecretAccessKey=""
AwsDefaultRegion=""

config_file_help() {
    echo "The Configuration File should have the following format:
            StackName=<Name for the Stack>
            KeyName=<EC2 Key Pair Name>
            PrivateKeyFilePath=<Path of the private key for the provided Key Pair name>
            AwsAccessKeyId=<AWS Access key>
            AwsSecretAccessKey=<AWS Secret Access Key>
            AwsDefaultRegion=<AWS Default Region>"
}

usage() {
    echo "Usage: . ./setup <ConfigFile>"
}

if [[ $# != 1 ]]; then
    usage
    exit 2
else
    source $1
fi

StackName="${StackName/$'\r'/}"
KeyName="${KeyName/$'\r'/}"
PrivateKeyFilePath="${PrivateKeyFilePath/$'\r'/}"
AwsAccessKeyId="${AwsAccessKeyId/$'\r'/}"
AwsSecretAccessKey="${AwsSecretAccessKey/$'\r'/}"
AwsDefaultRegion="${AwsDefaultRegion/$'\r'/}"

if [ -z "$StackName" ]; then
    echo "Missing StackName"
    config_file_help
    exit 2
fi

if [ -z "$KeyName" ]; then
    echo "Missing KeyName"
    config_file_help
    exit 2
fi

if [ -z "$PrivateKeyFilePath" ]; then
    echo "Missing PrivateKeyFilePath"
    config_file_help
    exit 2
fi

if [ -z "$AwsAccessKeyId" ]; then
    echo "Missing AwsAccessKeyId"
    config_file_help
    exit 2
fi

if [ -z "$AwsSecretAccessKey" ]; then
    echo "Missing AwsSecretAccessKey"
    config_file_help
    exit 2
fi

if [ -z "$AwsDefaultRegion" ]; then
    echo "Missing AwsDefaultRegion"
    config_file_help
    exit 2
fi

export AWS_ACCESS_KEY_ID="$AwsAccessKeyId"
export AWS_SECRET_ACCESS_KEY="$AwsSecretAccessKey"
export AWS_DEFAULT_REGION="$AwsDefaultRegion"
export ANSIBLE_HOST_KEY_CHECKING=false

pipenv install
pipenv shell
python scripts/ansible-setup.py --StackName "$StackName" --KeyName "$KeyName" --Region "$AwsDefaultRegion" --PrivateKeyFilePath "$PrivateKeyFilePath"
ansible-playbook -i ansible/hosts.ini ansible/DataGenerators.yaml
exit