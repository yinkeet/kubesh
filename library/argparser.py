import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from subprocess import call

class KubeshArgumentParser():
    def __init__(self, settings):
        self.settings = settings
        
    def __setup_environment_parsers(self, parent_parser):
        subparsers = parent_parser.add_subparsers(title='Environments', dest='environment', required=True, help='Environment/Helper')
        for id, setting in self.settings['environments'].items():
            parser = subparsers.add_parser(id, help=setting['description'])
            self.__setup_operation_parsers(parser, setting['type'])
        parser = subparsers.add_parser('docker', help='Docker helper.')
        self.__setup_docker_parsers(parser)
        parser = subparsers.add_parser('kubernetes', help='Kubernetes helper.')
        self.__setup_kubernetes_parsers(parser)
        parser = subparsers.add_parser('azure', help='Azure helper.')
        self.__setup_cloud_service_parsers(parser)
        parser = subparsers.add_parser('google', help='Google helper.')
        self.__setup_cloud_service_parsers(parser)

    def __setup_operation_parsers(self, parent_parser, type):
        subparsers = parent_parser.add_subparsers(title='Operations', dest='operation', required=True, help='Operation to execute')
        # Build
        parser = subparsers.add_parser('build', help='Build, tag and push image(s).')
        parser.add_argument('containers', nargs='*', help='Containers to build')
        # Config
        parser = subparsers.add_parser('config', help='Show deployment config yaml.')
        # Run
        parser = subparsers.add_parser('run', help='Run deployment.')
        parser.add_argument('containers', nargs='*', help='Containers to run')
        # Stop
        parser = subparsers.add_parser('stop', help='Stop deployment.')
        parser.add_argument('containers', nargs='*', help='Containers to stop')
        # Logs
        parser = subparsers.add_parser('logs', help='Show logs of container in deployment.')
        if type == 'docker':
            parser.add_argument('containers', nargs='+', help='Containers to show the logs')    
        else:
            parser.add_argument('pod', help='Pod to show the logs')    
            parser.add_argument('container', help='Container to show the logs')
        parser.add_argument('-f', '--follow', action='store_true', help='Follow log output')
        # SSH
        parser = subparsers.add_parser('ssh', help='Tunnel into container of the deployment.')
        if type != 'docker':
            parser.add_argument('pod', help='Pod to tunnel into')
        parser.add_argument('container', help='Container to tunnel into')
        parser.add_argument('command', help='Command to execute')
        parser.add_argument('args', nargs='*', help='Command arguments')

    def __setup_docker_parsers(self, parent_parser):
        subparsers = parent_parser.add_subparsers(title='Operations', dest='operation', required=True, help='Operation to execute')
        # Clean up
        parser = subparsers.add_parser('cleanup', help='Build, tag and push image(s).')
        parser.add_argument('containers', nargs='*', help='Containers to build')
        # Kill
        parser = subparsers.add_parser('kill', help='Removes stopped containers, followed by untagged images and then unused volumes.')
        parser.add_argument('containers', nargs='*', help='Forcefully removes all images.')

    def __setup_kubernetes_parsers(self, parent_parser):
        subparsers = parent_parser.add_subparsers(title='Operations', dest='operation', required=True, help='Operation to execute')
        # Image pull secret
        parser = subparsers.add_parser('image_pull_secret', help='Creates an image pull secret.')
        parser.add_argument('name', help='Environment name.')

    def __setup_cloud_service_parsers(self, parent_parser):
        subparsers = parent_parser.add_subparsers(title='Operations', dest='operation', required=True, help='Operation to execute')
        choices = []
        for id, setting in self.settings['environments'].items():
            if setting['type'] == 'kubernetes':
                choices.append(id)
        # Auth
        parser = subparsers.add_parser('auth', help='Authenticate this machine.')
        parser.add_argument('name', choices=choices, help='Environment name.')
        # Cluster
        parser = subparsers.add_parser('cluster', help='Switch cluster.')
        parser.add_argument('name', choices=choices, help='Environment name.')

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