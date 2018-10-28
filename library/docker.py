from subprocess import PIPE, call, check_output
from typing import List

from environment import Environment


class Docker(Environment):
    def build(self, containers: List[str]=[]):
        command = ['docker-compose', '-f', self.deployment_filename, 'build', '--force-rm']
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
