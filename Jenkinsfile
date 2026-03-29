pipeline {
    agent any

    environment {
        IMAGE_NAME      = 'etl-python'
        IMAGE_TAG       = "${BUILD_NUMBER}"
        ARTIFACTORY_URL = 'http://artifactory:8081/artifactory'
        ARTIFACTORY_REPO = 'python-docker'
        DB_HOST         = 'host.docker.internal'
        DB_PORT         = '3306'
        DB_NAME         = 'etl_db'
        DB_USER         = 'root'
        DB_PASS         = 'password'
    }

    stages {

        stage('Checkout') {
            steps {
                echo '📥 Pulling code from GitHub...'
                git branch: 'main',
                    url: 'https://github.com/abinashrout548/CICD.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                echo '📦 Installing Python dependencies...'
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                echo '🧪 Running pytest...'
                sh 'pytest test_etl.py -v'
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
                echo '📤 Pushing image to Artifactory...'
                sh """
                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} \
                        artifactory:8081/${ARTIFACTORY_REPO}/${IMAGE_NAME}:${IMAGE_TAG}
                    docker push \
                        artifactory:8081/${ARTIFACTORY_REPO}/${IMAGE_NAME}:${IMAGE_TAG}
                """
            }
        }

        stage('Deploy & Run ETL') {
            steps {
                echo '🚀 Running ETL container...'
                sh """
                    docker stop ${IMAGE_NAME} || true
                    docker rm   ${IMAGE_NAME} || true
                    docker run --name ${IMAGE_NAME} \
                        --network artifactory-net \
                        -e DB_HOST=${DB_HOST} \
                        -e DB_PORT=${DB_PORT} \
                        -e DB_NAME=${DB_NAME} \
                        -e DB_USER=${DB_USER} \
                        -e DB_PASS=${DB_PASS} \
                        ${IMAGE_NAME}:${IMAGE_TAG}
                """
            }
        }
    }

    post {
        success {
            echo '✅ ETL Pipeline completed successfully!'
        }
        failure {
            echo '❌ ETL Pipeline failed! Check the logs above.'
        }
    }
}
