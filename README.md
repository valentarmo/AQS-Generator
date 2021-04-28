# AQS Generators
Generate random simulated air quality data from ten EC2 instances for [AQS](https://github.com/valentarmo/AQS). Meant to be automatically deployed by the Jenkins server from [AQS-Builder](https://github.com/valentarmo/AQS-Builder).

## Infrastructure Testing
The CloudFormation stack can be tested using taskcat. To do it, an appropriate `.taskcat.yml` file can be generated using `scripts/create-taskcat-file.py`. It will generate the `.taskcat.yml` file in the project's root folder.

    $ python scripts/create-taskcat-file.py \
        --Region <AWS Region> \
        --KeyName <EC2 Key Pair Name>
    $ taskcat test run

## Deployment
The deployment is performed using CloudFormation, Ansible and python scripts. The current deployment process assumes there is an S3 Bucket with the .pem file of the EC2 key pair used to create the EC2 instances.

### Infrastructure deployment
To generate the CloudFormation template use `scripts/generate-cfn-template.py`

    $ python scripts/generate-cfn-template.py --NumberOfInstances <#>

To ease the infrastructure's deployment `scripts/deploy-infrastructure.py` can be used. It will generate an appropriate host file for Ansible to proceed with the system configuration.

    $ python scripts/deploy-infrastructure.py \
            --StackName <Name for the Stack> \
            --Region <AWS Region> \
            --KeyName <EC2 Key Pair Name> \
            --PrivateKeyS3Bucket <S3 Bucket With the EC2 Key> \
            --PrivateKeyS3Path <.pem File path inside the S3 Bucket>

### Hosts Configuration
This task is performed by ansible using the `ansible/InfrastructureConfiguration` playbook.

    $ ansible-playbook -i ansible/hosts.ini \
        ansible/InfrastructureConfiguration.yaml


### Generator Script Deployment
The deployment of the script is performed with Ansible using the `ansible/ApplicationDeployment.yaml` playbook, and it relies on the generator's docker image being in Docker Hub.

    $ docker build --tag <Docker User>/<Image Tag> .
    $ docker push <Docker User>/<Image Tag>
    $ ansible playbook -i ansible/hosts.ini \
        ansible/ApplicationDeployment.yaml