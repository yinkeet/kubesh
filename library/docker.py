import os
import sys
from subprocess import PIPE, call, check_output
from typing import List

from library.environment import Environment, NameFactory


class Docker(Environment):
    def __init__(self, info: dict, templates: dict):
        super().__init__(info, templates)
        self.image_name_factory = NameFactory(
            self.templates.get('docker_image_name', '__DIRECTORY_NAME_____CONTAINER__')
        )

    def _build_command(self, command) -> List[str]:
        if isinstance(self.deployment_filename, str):
            base = ['docker-compose', '-f', self.deployment_filename]
        elif isinstance(self.deployment_filename, list) and list:
            base = ['docker-compose']
            for deployment_filename in self.deployment_filename:
                base.extend(['-f', deployment_filename])
        else:
            raise ValueError('deployment_filename should be str or list')
        if isinstance(command, str):
            base.append(command)
        elif isinstance(command, list) and list:
            base.extend(command)
        else:
            raise ValueError('command should be str or list')
        return base

    def build(self, containers: List[str]=[]):
        command = self._build_command('build')
        if containers:
            command.extend(containers)
        call(command)
    
    def config(self):
        print('')
        call(self._build_command('config'))

    def run(self, containers: List[str]=[]):
        command = self._build_command(['up', '-d'])
        if containers:
            command.extend(containers)
        call(command)

    def clean_up(self, containers: List[str]=[]):
        untagged_images = []
        for container in containers:
            image_name = self.image_name_factory.make({'__DIRECTORY_NAME__': os.getcwd().split(os.sep)[-1], '__CONTAINER__': container})
            untagged_images.extend (
                check_output(
                    ['docker', 'images', image_name, '-f', 'dangling=true', '-q']
                ).decode('UTF-8').splitlines()
            )
            
        if untagged_images:
            command = ['docker', 'rmi']
            command.extend(untagged_images)
            call(command, stdout=PIPE)    
        else:
            print('Nothing to clean')

    def stop(self, containers: List[str]=[]):
        command = self._build_command('stop')
        if containers:
            command.extend(containers)
        call(command)

    def logs(self, containers: List[str]=[], pod: str=None, container: str=None, follow: bool=False):
        command = self._build_command('logs')
        if follow:
            command.append('-f')
        if containers:
            command.extend(containers)
        try:
            call(command, stderr=PIPE)
        except KeyboardInterrupt:
            sys.exit(0)

    def ssh(self, pod: str=None, container: str=None, command: str=None, args: List[str]=[]):
        command = self._build_command(['exec', container, command])
        if args:
            command.extend(args)
        call(command)
