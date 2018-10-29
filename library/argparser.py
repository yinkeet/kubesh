import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from subprocess import call

from common import get_containers, get_services


class KubeshArgumentParser():
    def __init__(self, settings):
        self.settings = settings
        
    def __setup_environment_parsers(self, parent_parser):
        subparsers = parent_parser.add_subparsers(title='Environments', dest='environment', help='Environment')
        for id, setting in self.settings['environments'].items():
            parser = subparsers.add_parser(id, help=setting['description'])
            if type == 'docker':
                containers = get_services(setting['deployment_filename'])
            else:
                containers = get_containers(setting['dockerfile_filename'])
            self.__setup_operation_parsers(parser, setting['type'], containers)

    def __setup_operation_parsers(self, parent_parser, type, containers):
        subparsers = parent_parser.add_subparsers(title='Operations', dest='operation', help='Operation to execute')
        # Build
        parser = subparsers.add_parser('build', help='Build, tag and push image(s).')
        parser.add_argument('containers', nargs='*', help='Containers to build')
        # Config
        parser = subparsers.add_parser('config', help='Show deployment config yaml.')
        # Image pull secret
        if type == 'kubernetes':
            parser = subparsers.add_parser('image_pull_secret', help='Creates an image pull secret.')
        # Run
        parser = subparsers.add_parser('run', help='Run deployment.')
        parser.add_argument('containers', nargs='*', help='Containers to run')
        # Remove untagged images
        parser = subparsers.add_parser('clean_up', help='Remove untagged images.')
        parser.add_argument('containers', nargs='*', help='Containers to clean')
        # Stop
        parser = subparsers.add_parser('stop', help='Stop deployment.')
        parser.add_argument('containers', nargs='*', help='Containers to stop')
        # Logs
        parser = subparsers.add_parser('logs', help='Show logs of container in deployment.')
        if type == 'docker':
            parser.add_argument('containers', nargs='+', choices=containers, help='Containers to show the logs')    
        else:
            parser.add_argument('pod', help='Pod to show the logs')    
            parser.add_argument('container', choices=containers, help='Container to show the logs')
        parser.add_argument('-f', '--follow', action='store_true', help='Follow log output')
        # SSH
        parser = subparsers.add_parser('ssh', help='Tunnel into container of the deployment.')
        if type != 'docker':
            parser.add_argument('pod', help='Pod to tunnel into')
        parser.add_argument('container', choices=containers, help='Container to tunnel into')
        parser.add_argument('command', help='Command to execute')
        parser.add_argument('args', nargs='*', help='Command arguments')
        # Auth and cluster
        if type == 'kubernetes':
            # Auth
            subparsers.add_parser('auth', help='Authenticate this machine.')
            # Cluster
            subparsers.add_parser('cluster', help='Switch cluster.')

    def run(self):
        parser = ArgumentParser(
            formatter_class=RawDescriptionHelpFormatter,
            epilog='''
Clipboard:
  Starting minikube: 
    minikube start && eval $(minikube docker-env)
  Stopping minikube: 
    minikube stop && eval $(minikube docker-env -u)
            '''
        )
        self.__setup_environment_parsers(parser)
        return parser.parse_args()
