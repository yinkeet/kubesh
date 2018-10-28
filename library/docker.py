import os
from subprocess import PIPE, call, check_output
from typing import List

from common import Condition, WrapPrint, generate_image_name, get_services
from environment import Environment


class Docker(Environment):
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
            image_name = os.getcwd().split(os.sep)[-1] + '_' + container
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
        call(command)

    def ssh(self, pod: str=None, container: str=None, command: str=None, args: List[str]=[]):
        command = ['docker-compose', '-f', self.deployment_filename, 'exec', container, command]
        if args:
            command.extend(args)
        call(command)

    @staticmethod
    def cleanup():
        Docker.remove_stopped_containers()
        Docker.remove_untagged_images()
        Docker.remove_unused_volumes()

    @staticmethod
    def remove_stopped_containers():
        print('Removing stopped containers... ', end='', flush=True)
        stopped_containers = check_output(
            ['docker', 'ps', '-a', '-f', 'status=exited', '-q']
        ).decode('UTF-8').splitlines()
        
        if stopped_containers:
            command = ['docker', 'rm']
            command.extend(stopped_containers)
            call(command, stdout=PIPE)
        print('done')

    @staticmethod
    def remove_untagged_images():
        print('Removing untagged images... ', end='', flush=True)
        call(['docker', 'image', 'prune', '-f'], stdout=PIPE)
        print('done')

    @staticmethod
    def remove_unused_volumes():
        print('Removing unused volumes... ', end='', flush=True)
        call(['docker', 'volume', 'prune', '-f'], stdout=PIPE)
        print('done')

    @staticmethod
    def kill():
        print('Killing all images... ', end='', flush=True)
        call(['docker', 'image', 'prune', '-a', '-f'], stdout=PIPE)
        print('done')
