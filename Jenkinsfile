Pipeline {
    agent any

    environment {
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
        DOCKER_CREDENTIALS = credentials('docker-credentials')
    } 
    stages {
        stage('Intall application dependencies') {
            steps {
                echo 'Installing Application dependencies'
                sh 'pipenv install'
                echo 'Finished Installing Application dependencies'
            }
        }
        stage('Test application') {
            steps {
                echo 'Starting Application Tests'
                sh 'pipenv shell'
                sh 'python ./src/test_DataGenerator'
                sh 'exit'
                echo 'Finished Application Tests'
            }
        }
        stage('Build Docker Image') {
            when {
                expression {
                    currentBuild.result == 'SUCCESS'
                }
            }
            steps {
                echo 'Building Docker Image'
                sh 'docker login -u ${env.DOCKER_CREDENTIALS_USR} -p ${env.DOCKER_CREDENTIALS_PSW}'
                sh 'docker build --tag AQSDataGenerator:latest .'
                echo 'Finished Building Docker Image'
            }
        }
        stage('Publish Docker Image') {
            when {
                expression {
                    currentBuild.result == 'SUCCESS'
                }
            }
            steps {
                echo 'Publishing Docker Image'
                sh 'docker push ${env.DOCKER_CREDENTIALS_USR}/AQSDataGenerator:latest'
                echo 'Finished Publishing Docker Image'
            }
        }
        stage('Test infrastructure') {
            steps {
                echo 'Starting Infrastructure Tests'
                sh 'python ./scripts/create-task-file.py --Region ${env.AWS_DEFAULT_REGION} --KeyName ${env.AQS_GENERATORS_KEY_NAME}'
                sh 'taskcat test run'
                echo 'Finished Infrastructure Tests'
            }
        }
        stage('Deploy Infrastructure') {
            when {
                expression {
                    currentBuild.result == 'SUCCESS'
                }
            }
            steps {
                echo 'Starting Infrastructure Deployment'
                sh 'pipenv shell'
                sh 'python ./scripts/deploy-infrastructure.py --StackName ${env.AQS_GENERATORS_STACK_NAME} --KeyName ${env.AQS_GENERATORS_KEY_NAME} --Region ${env.AQS_GENERATORS_REGION} --PrivateKeyS3Bucket ${env.AQS_GENERATORS_KEY_S3_BUCKET} --PrivateKeyS3FilePath ${env.AQS_GENERATORS_KEY_S3_PATH}'
                sh 'exit'
                echo 'Finished Infrastructure Deployment'
            }
        }
        stage('Configure Infrastructure') {
            when {
                expression {
                    currentBuild.result == 'SUCCESS'
                }
            }
            steps {
                echo 'Starting Infrastructure Configuration'
                sh 'ansible-playbook -i ansible/hosts.ini ansible/InfrastructureConfiguration.yaml'
                echo 'Finished Infrastructure Configuration'
            }
        }
        stage('Deploy Application') {
            when {
                expression {
                    currentBuild.result == 'SUCCESS'
                }
            }
            steps {
                echo 'Starting Application Deployment'
                sh 'ansible-playbook -i ansible/hosts.ini ansible/ApplicationDeployment.yaml'
                echo 'Finished Application Deployment'
            }
        }
    }
}