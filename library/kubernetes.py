import os
import sys
from abc import abstractmethod
from subprocess import PIPE, call, check_output, run

from library.common import WrapPrint, load_deployment_file, load_environment_variables
from library.environment import Environment


class Kubernetes(Environment):
    @abstractmethod
    def get_build_image_name(self, container: str) -> str:
        pass

    @abstractmethod
    def get_deployment_image_name(self, container: str) -> str:
        pass

    @abstractmethod
    def container_built_and_pushed(self, container: str) -> bool:
        pass

    def build(self, containers):
        for container in containers:
            image_name = self.get_build_image_name(container)
            if not (self.production and self.container_built_and_pushed(container)):
                call(['docker', 'build', '--force-rm', '--no-cache', '--rm', '--file', container + '/' + self.dockerfile_filename, '-t', image_name, os.getcwd() + '/' + container])
                call(['docker', 'push', image_name])
            else:
                print('Image ' + image_name + ' has already been built and pushed to the cloud.')

    @WrapPrint('Loading image names... ', 'done')
    def _load_image_names(self, containers):
        for container in containers:
            os.environ[container.upper() + '_IMAGE_NAME'] = self.get_deployment_image_name(container)
    
    def config(self, containers):
        self._load_image_names(containers)
        print('\n' + load_deployment_file(self.deployment_filename) + '\n')

    @WrapPrint('Creating image pull secret... ', 'done')
    def image_pull_secret(self):
        variables = load_environment_variables([
            'IMAGE_PULL_SECRET_NAME', 'IMAGE_PULL_SECRET_SERVER', 'IMAGE_PULL_SECRET_USERNAME', 'IMAGE_PULL_SECRET_PASSWORD', 'IMAGE_PULL_SECRET_EMAIL'
        ])
        name = variables['IMAGE_PULL_SECRET_NAME']
        server = variables['IMAGE_PULL_SECRET_SERVER']
        username = variables['IMAGE_PULL_SECRET_USERNAME']
        password = variables['IMAGE_PULL_SECRET_PASSWORD']
        email = variables['IMAGE_PULL_SECRET_EMAIL']
        data = check_output(['kubectl', 'create', 'secret', 'docker-registry', name, '--docker-server', server, '--docker-username', username, '--docker-password', password, '--docker-email', email, '--dry-run', '-o', 'yaml']).decode('UTF-8')
        run(['kubectl', 'apply', '-f', '-'], input=data, encoding='UTF-8', stdout=PIPE)

    def run(self, containers):
        self._load_image_names(containers)
        run(['kubectl', 'apply', '-f', '-'], input=load_deployment_file(self.deployment_filename), encoding='UTF-8')

    def stop(self, containers):
        self._load_image_names(containers)
        run(['kubectl', 'delete', '-f', '-'], input=load_deployment_file(self.deployment_filename), encoding='UTF-8')

    def namespace(self):
        current_context = check_output(['kubectl', 'config', 'current-context']).decode('UTF-8').replace('\n', '')
        call(['kubectl', 'config', 'set-context', current_context, '--namespace=' + os.getenv('NAMESPACE')])

    def logs(self, containers=[], pod=None, container=None, follow=False):
        command = ['kubectl', 'logs', pod, container]
        if follow:
            command.append('-f')
        try:
            call(command)
        except KeyboardInterrupt:
            print('')
            sys.exit(0)

    def ssh(self, pod=None, container=None, command=None, args=None):
        command = ['kubectl', 'exec', '-it', pod, '--container=' + container, '--', command]
        if args:
            command.extend(args)
        call(command)

    @abstractmethod
    def auth(self):
        pass

    @abstractmethod
    def cluster(self):
        pass