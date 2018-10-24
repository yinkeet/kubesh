import os
import sys
from subprocess import PIPE, CalledProcessError, call, check_output, run
from time import sleep

import requests

from common import load_environment_variables
from kubernetes import Kubernetes


class GKE(Kubernetes):
    def image_name_template(self):
        return self.templates['google_image_name']
    
    def get_image_name_with_digest(self, image_name: str):
        return image_name + '@123'
    
    def __get_image_name_with_digest(self, image_name):
        return check_output(['docker', 'image', 'inspect', image_name + ':latest', '-f', '{{index .RepoDigests 0}}']).decode('UTF-8')

    def __load_image_names(self, containers=[]):
        variables = load_environment_variables(['AZURE_CONTAINER_REGISTRY_NAME'])
        print('Loading image names... ', end='', flush=True)
        if not containers:
            containers = self.__get_containers()
        for container in containers:
            image_name = self.__generate_image_names(container)
            # az acr repository show --name bambu --image node-boilerplate/test/node:latest --query 'digest' --output tsv
            image_name += '@' + check_output(['az', 'acr', 'repository', 'show', '--name', variables['AZURE_CONTAINER_REGISTRY_NAME'], '--image', image_name + ':latest', '--query', 'digest', '--output', 'tsv']).decode('UTF-8').replace('\n', '')
            os.environ[container.upper() + '_IMAGE_NAME'] = image_name
        print('done')

    def stop(self, containers=[]):
        self.__minikube_health_checker()

        self.__load_image_names(containers)

        data = self.__load_deployment_file()

        # Stop the deployment
        print('Stopping deployment...')
        run(['kubectl', 'delete', '-f', '-'], input=data, encoding='UTF-8')
        print('done')

    def logs(self, containers=[], pod=None, container=None, follow=False):
        self.__minikube_health_checker()
        command = ['kubectl', 'logs', pod, container]
        if follow:
            command.append('-f')
        try:
            call(command)
        except KeyboardInterrupt:
            print('')
            sys.exit(0)

    def ssh(self, pod=None, container=None, command=None, args=None):
        self.__minikube_health_checker()
        command = ['kubectl', 'exec', '-it', pod, '--container=' + container, '--', command]
        if args:
            command.extend(args)
        call(command)

    def url(self):
        self.__minikube_health_checker()
        print('http://' + check_output(['minikube', 'ip']).decode('UTF-8').replace('\n', '') + '/')
