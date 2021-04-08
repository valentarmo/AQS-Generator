pipeline {
    agent any

    environment {
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
        DOCKER_CREDENTIALS = credentials('docker-credentials')
    } 
    stages {
        stage('Test application') {
            steps {
                withEnv(['PATH+EXTRA=/usr/local/bin']) {
                    echo 'Starting Application Tests'
                    sh 'python3 ./src/test_DataGenerator.py'
                    echo 'Finished Application Tests'
                }
            }
        }
        stage('Build Docker Image') {
            steps {
                echo 'Building Docker Image'
                sh 'docker login -u $DOCKER_CREDENTIALS_USR -p $DOCKER_CREDENTIALS_PSW'
                sh 'docker build --tag AQSDataGenerator:latest .'
                echo 'Finished Building Docker Image'
            }
        }
        stage('Publish Docker Image') {
            steps {
                echo 'Publishing Docker Image'
                sh 'docker push $DOCKER_CREDENTIALS_USR/AQSDataGenerator:latest'
                echo 'Finished Publishing Docker Image'
            }
        }
        stage('Test infrastructure') {
            steps {
                withEnv(['PATH+EXTRA=/usr/local/bin']) {
                    echo 'Starting Infrastructure Tests'
                    sh "python3 ./scripts/create-taskcat-file.py --Region ${env.AWS_DEFAULT_REGION} --KeyName ${env.AQS_GENERATORS_KEY_NAME}"
                    sh 'taskcat test run'
                    echo 'Finished Infrastructure Tests'
                }
            }
        }
        stage('Deploy Infrastructure') {
            steps {
                withEnv(['PATH+EXTRA=/usr/local/bin']) {
                    echo 'Starting Infrastructure Deployment'
                    sh "python3 ./scripts/deploy-infrastructure.py --StackName ${env.AQS_GENERATORS_STACK_NAME} --KeyName ${env.AQS_GENERATORS_KEY_NAME} --Region ${env.AQS_GENERATORS_REGION} --PrivateKeyS3Bucket ${env.AQS_GENERATORS_KEY_S3_BUCKET} --PrivateKeyS3FilePath ${env.AQS_GENERATORS_KEY_S3_PATH}"
                    echo 'Finished Infrastructure Deployment'
                }
            }
        }
        stage('Configure Infrastructure') {
            steps {
                echo 'Starting Infrastructure Configuration'
                sh 'ansible-playbook -i ansible/hosts.ini ansible/InfrastructureConfiguration.yaml'
                echo 'Finished Infrastructure Configuration'
            }
        }
        stage('Deploy Application') {
            steps {
                echo 'Starting Application Deployment'
                sh 'ansible-playbook -i ansible/hosts.ini ansible/ApplicationDeployment.yaml'
                echo 'Finished Application Deployment'
            }
        }
    }
}