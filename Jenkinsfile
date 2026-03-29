pipeline {
    agent any

    environment {
        IMAGE_NAME = 'cicd-python'
        IMAGE_TAG  = "${BUILD_NUMBER}"
        ARTIFACTORY_URL = 'http://artifactory:8081/artifactory'
    }

    stages {
        stage('Checkout') {
            steps {
                echo '📥 Pulling from GitHub...'
                git branch: 'main',
                    url: 'https://github.com/abinashrout548/CICD.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                echo '📦 Installing dependencies...'
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                echo '🧪 Running tests...'
                sh 'pytest test_script.py -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image...'
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }

        stage('Push to Artifactory') {
            steps {
                echo '📤 Pushing to Artifactory...'
                sh """
                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} \
                    artifactory:8081/python-docker/${IMAGE_NAME}:${IMAGE_TAG}
                    docker push \
                    artifactory:8081/python-docker/${IMAGE_NAME}:${IMAGE_TAG}
                """
            }
        }

        stage('Deploy') {
            steps {
                echo '🚀 Deploying container...'
                sh """
                    docker stop ${IMAGE_NAME} || true
                    docker rm ${IMAGE_NAME} || true
                    docker run -d \
                        --name ${IMAGE_NAME} \
                        --network artifactory-net \
                        ${IMAGE_NAME}:${IMAGE_TAG}
                """
            }
        }
    }

    post {
        success { echo '✅ Pipeline succeeded!' }
        failure { echo '❌ Pipeline failed! Check logs.' }
    }
}