import os
import sys
from subprocess import PIPE, call, check_output
from typing import List

from common import Condition, WrapPrint, generate_image_name, get_services
from environment import Environment


class Docker(Environment):
    @property
    def image_name_template(self):
        return self.templates.get('docker_image_name', '__DIRECTORY_NAME_____CONTAINER__')

    def build(self, containers: List[str]=[]):
        command = ['docker-compose', '-f', self.deployment_filename, 'build']
        if containers:
            command.extend(containers)
        call(command)
    
    def config(self):
        print('')
        command = ['docker-compose', '-f', self.deployment_filename, 'config']
        call(command)

    def run(self, containers: List[str]=[]):
        command = ['docker-compose', '-f', self.deployment_filename, 'up', '-d']
        if containers:
            command.extend(containers)
        call(command)

    @Condition('containers', get_services, 'deployment_filename')
    def clean_up(self, containers: List[str]=[]):
        untagged_images = []
        for container in containers:
            image_name = self.image_name_template.replace('__DIRECTORY_NAME__', os.getcwd().split(os.sep)[-1]).replace('__CONTAINER__', container)
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
        command = ['docker-compose', '-f', self.deployment_filename, 'stop']
        if containers:
            command.extend(containers)
        call(command)

    def logs(self, containers: List[str]=[], pod: str=None, container: str=None, follow: bool=False):
        command = ['docker-compose', '-f', self.deployment_filename, 'logs']
        if follow:
            command.append('-f')
        if containers:
            command.extend(containers)
        try:
            call(command)
        except KeyboardInterrupt:
            sys.exit(0)

    def ssh(self, pod: str=None, container: str=None, command: str=None, args: List[str]=[]):
        command = ['docker-compose', '-f', self.deployment_filename, 'exec', container, command]
        if args:
            command.extend(args)
        call(command)
