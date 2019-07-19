pipeline {
    agent any

    environment {
        FULL_DOCKER_IMAGE_NAME = 'thevirtualbrain/tvb-run'
        PY2_TAG = 'tvb-library-py2'
        PY3_TAG = 'tvb-library-py3'
    }

    stages {
        stage ('Run tests in python 2 environment') {
            agent {
                docker {
                    image '${FULL_DOCKER_IMAGE_NAME}:${PY2_TAG}'
                }
            }
            steps {
                sh '''#!/bin/bash
                    source activate tvb-run
                    pytest --cov-config .coveragerc --cov=tvb tvb/tests --cov-branch --cov-report xml:TEST_OUTPUT/coverage_library.xml --junitxml=TEST_OUTPUT/TEST-LIBRARY-RESULTS.xml
                '''
                junit 'TEST_OUTPUT/TEST-LIBRARY-RESULTS.xml'
                step([$class: 'CoberturaPublisher', autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'TEST_OUTPUT/coverage_library.xml', failUnhealthy: false, failUnstable: false, maxNumberOfBuilds: 0, onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false])
            }
        }

        stage ('Run tests in python 3 environment') {
            agent {
                docker {
                    image '${FULL_DOCKER_IMAGE_NAME}:${PY3_TAG}'
                }
            }
            steps {
                sh '''#!/bin/bash
                    source activate tvb-run
                    pytest --cov-config .coveragerc --cov=tvb tvb/tests --cov-branch --cov-report xml:TEST_OUTPUT/coverage_library.xml --junitxml=TEST_OUTPUT/TEST-LIBRARY-RESULTS.xml
                '''
                junit 'TEST_OUTPUT/TEST-LIBRARY-RESULTS.xml'
                step([$class: 'CoberturaPublisher', autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'TEST_OUTPUT/coverage_library.xml', failUnhealthy: false, failUnstable: false, maxNumberOfBuilds: 0, onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false])
            }
        }
    }

    post {
        changed {
            mail to: 'paula.popa@codemart.ro',
            subject: "Jenkins Pipeline ${currentBuild.fullDisplayName} changed status",
            body: """
                Result: ${currentBuild.result}
                Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'
                Check console output at ${env.BUILD_URL}"""
        }

        success {
            echo 'Build finished successfully'
        }
    }
}