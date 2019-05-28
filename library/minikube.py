import os
import sys
from subprocess import PIPE, CalledProcessError, call, check_output, run
from time import sleep
from typing import List

from library.common import WrapPrint, load_deployment_file, minikube_health_checker
from library.environment import Environment, NameFactory


class Minikube(Environment):
    def __init__(self, info: dict, templates: dict):
        super().__init__(info, templates)
        self.image_name_factory = NameFactory(
            self.templates.get('minikube_image_name', 'localhost:5000/$NAMESPACE/$APP/__CONTAINER__') + ':latest'
        )

    @minikube_health_checker
    def build(self, containers=[]):

        @WrapPrint('Starting local registry... ', 'done')
        def start_local_registry():
            call(['docker', 'run', '-d', '-p', '5000:5000', '--name', 'registry', 'registry:2'], stdout=PIPE)
            # Local registry health check
            while call(['curl', '-s', 'http://' + check_output(['minikube', 'ip']).decode('UTF-8').replace('\n', '') + ':5000']):
                sleep(0.1)

        @WrapPrint('Stopping local registry... ', 'done')
        def stop_local_registry():
            call(['docker', 'stop', 'registry'], stdout=PIPE)
            call(['docker', 'rm', 'registry'], stdout=PIPE)

        start_local_registry()
        # Build and push images to local registry
        for container in containers:
            image_name = self.image_name_factory.make({'__CONTAINER__': container})
            call(['docker', 'build', '--force-rm', '--rm', '--file', container + '/' + self.dockerfile_filename, '-t', image_name, os.getcwd() + '/' + container])
            call(['docker', 'push', image_name])
        stop_local_registry()

    @WrapPrint('Loading image names... ', 'done')
    def _load_image_names(self, containers):
        for container in containers:
            image_name = self.image_name_factory.make({'__CONTAINER__': container})
            try:
                os.environ[container.upper() + '_IMAGE_NAME'] = check_output(['docker', 'image', 'inspect', image_name, '-f', '{{index .RepoDigests 0}}']).decode('UTF-8').replace('\n', '')
            except CalledProcessError as e:
                pass

    @minikube_health_checker
    def config(self, containers):
        self._load_image_names(containers)
        print('\n' + load_deployment_file(self.deployment_filename) + '\n')
        
    @minikube_health_checker
    def run(self, containers):
        self._load_image_names(containers)
        run(['kubectl', 'apply', '-f', '-'], input=load_deployment_file(self.deployment_filename), encoding='UTF-8')

    @minikube_health_checker
    @WrapPrint('Cleaning up... ', 'done')
    def clean_up(self, containers: List[str]):
        untagged_images = []
        for container in containers:
            image_name = self.image_name_factory.make({'__CONTAINER__': container})
            untagged_images.extend (
                check_output(
                    ['docker', 'images', image_name, '-f', 'dangling=true', '-q']
                ).decode('UTF-8').splitlines()
            )
            
        if untagged_images:
            command = ['docker', 'rmi']
            command.extend(untagged_images)
            call(command, stdout=PIPE)

    @minikube_health_checker
    def stop(self, containers):
        self._load_image_names(containers)
        run(['kubectl', 'delete', '-f', '-'], input=load_deployment_file(self.deployment_filename), encoding='UTF-8')

    @minikube_health_checker
    def namespace(self):
        current_context = check_output(['kubectl', 'config', 'current-context']).decode('UTF-8').replace('\n', '')
        call(['kubectl', 'config', 'set-context', current_context, '--namespace=' + os.getenv('NAMESPACE')])

    @minikube_health_checker
    def logs(self, containers=[], pod=None, container=None, follow=False):
        command = ['kubectl', 'logs', pod, container]
        if follow:
            command.append('-f')
        try:
            call(command)
        except KeyboardInterrupt:
            print('')
            sys.exit(0)

    @minikube_health_checker
    def ssh(self, pod=None, container=None, command=None, args=None):
        command = ['kubectl', 'exec', '-it', pod, '--container=' + container, '--', command]
        if args:
            command.extend(args)
        call(command)
