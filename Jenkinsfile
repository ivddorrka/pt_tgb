pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/ivddorrka/pt_tgb.git'
            }
        }
        
        stage('Install dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        
        stage('Run tests') {
            steps {
                sh 'python -m unittest discover tests'
            }
        }
        
        stage('Deploy') {
            steps {
                sh 'python app.py'  // Or any other command to start your Flask app
            }
        }
    }
}

