import os
import sys
import yaml
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from subprocess import call


class KubeshArgumentParser():
    def __init__(self, settings):
        self.settings = settings

        self.__parser = ArgumentParser(
            formatter_class=RawDescriptionHelpFormatter,
            epilog='''
Clipboard:
  Starting minikube: 
    minikube start && eval $(minikube docker-env)
  Stopping minikube: 
    minikube stop && eval $(minikube docker-env -u)
            '''
        )
        self.__setup_environment_parsers()
        
    def __setup_environment_parsers(self):
        subparsers = self.__parser.add_subparsers(title='Environments', dest='environment', required=True, help='Environment')
        for id, setting in self.settings['environments'].items():
            parser = subparsers.add_parser(id, help=setting['description'])
            self.__setup_operation_parsers(parser, setting['type'], setting['containers']['all'], setting['containers']['buildable'])

    def __setup_operation_parsers(self, parent_parser, type, all_containers, buildable_containers):
        subparsers = parent_parser.add_subparsers(title='Operations', dest='operation', required=True, help='Operation to execute')
        
        # Build
        parser = subparsers.add_parser('build', help='Build, tag and push image(s).')
        parser.add_argument('-c', '--containers', nargs='+', choices=buildable_containers, default=buildable_containers, help='Containers to build')
        
        # Config
        parser = subparsers.add_parser('config', help='Show deployment config yaml.')
        if type != 'docker':
            parser.add_argument('--containers', action='store_const', const=False, default=buildable_containers)
        
        # Image pull secret
        if type == 'kubernetes':
            parser = subparsers.add_parser('image_pull_secret', help='Creates an image pull secret.')
        
        if type == 'docker':
            containers = all_containers
        else:
            containers = buildable_containers
            
        # Run
        parser = subparsers.add_parser('run', help='Run deployment.')
        parser.add_argument('-c', '--containers', nargs='+', choices=containers, default=containers, help='Containers to run')
        
        # Remove untagged images
        parser = subparsers.add_parser('clean_up', help='Remove untagged images.')
        parser.add_argument('-c', '--containers', nargs='+', choices=all_containers, default=all_containers, help='Containers to clean')
        
        # Stop
        parser = subparsers.add_parser('stop', help='Stop deployment.')
        parser.add_argument('-c', '--containers', nargs='+', choices=containers, default=containers, help='Containers to stop')
        
        # Namespace
        if type != 'docker':
            parser = subparsers.add_parser('namespace', help='Sets kubectl to the environment\'s namespace.')
        
        # Logs
        parser = subparsers.add_parser('logs', help='Show logs of container in deployment.')
        if type == 'docker':
            parser.add_argument('containers', nargs='+', choices=all_containers, help='Containers to show the logs')    
        else:
            parser.add_argument('pod', help='Pod to show the logs')    
            parser.add_argument('container', choices=all_containers, help='Container to show the logs')
        parser.add_argument('-f', '--follow', action='store_true', help='Follow log output')
        
        # SSH
        parser = subparsers.add_parser('ssh', help='Tunnel into container of the deployment.')
        if type != 'docker':
            parser.add_argument('pod', help='Pod to tunnel into')
        parser.add_argument('container', choices=all_containers, help='Container to tunnel into')
        parser.add_argument('command', help='Command to execute')
        parser.add_argument('args', nargs='*', help='Command arguments')
        
        # Auth and cluster
        if type == 'kubernetes':
            # Auth
            subparsers.add_parser('auth', help='Authenticate this machine.')
            # Cluster
            subparsers.add_parser('cluster', help='Switch cluster.')

    def run(self):
        return self.__parser.parse_args()
