import os
from functools import partial, wraps
from subprocess import CalledProcessError, check_output
from sys import exit

import yaml
from dotenv import load_dotenv


class WrapPrint(object):
    def __init__(self, prefix, suffix):
        self.prefix = prefix
        self.suffix = suffix

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            print(self.prefix, end='', flush=True)
            result = func(*args,**kwargs)
            print(self.suffix)
            return result
        return wrapper

def load_environment_file(filename: str):
    # Load general .env file
    env_path = os.getcwd() + '/.env'
    load_dotenv(dotenv_path=env_path, override=True)
    # Load specific .env file
    env_path = os.getcwd() + '/' + filename
    load_dotenv(dotenv_path=env_path, override=True)

def load_environment_variables(variables=[]):
    failed = False
    
    results = {}
    for variable in variables:
        value = os.getenv(variable)
        if value is None:
            failed = True
            print(variable + ' is not set')
        else:
            results[variable] = value

    if failed:
        exit(1)
    
    return results

@WrapPrint('Loading deployment file... ', 'done')
def load_deployment_file(deployment_filename: str):
    with open(deployment_filename, 'r') as deployment_file:
        data = deployment_file.read()
    return os.path.expandvars(data)

def minikube_health_checker(func):
    def wrapper(*args, **kwargs):
        try:
            status = check_output(['minikube', 'status', '--format', '{{.Host}}']).decode('UTF-8')
        except CalledProcessError as error:
            status = error.output.decode('UTF-8')
        if status != 'Running':
            print('Minikube is not running, start it by running this command:')
            print('minikube start && eval $(minikube docker-env)')
            exit(1)
        func(*args, **kwargs)
    return wrapper

def get_services(deployment_filename: str):
    with open(deployment_filename, 'r') as stream:
        try:
            return [service for service, details in yaml.load(stream, Loader=yaml.Loader)['services'].items()]
        except yaml.YAMLError as error:
            print(error)
            exit(1)

def get_containers(dockerfile_filename):
    return check_output(
        ['find', '.', '-type', 'f', '-maxdepth', '2', '-mindepth' ,'2', '-name', dockerfile_filename]
    ).decode('UTF-8').replace('./', '').replace('/' + dockerfile_filename, '').splitlines()

def get_containers_from_yaml(deployment_filename):
    containers = []
    with open(deployment_filename, 'r') as stream:
        for data in yaml.safe_load_all(stream):
            if 'kind' in data and data['kind'] == 'Deployment':
                try:
                    spec = data['spec']['template']['spec']
                    if 'initContainers' in spec:
                        for container in spec['initContainers']:
                            containers.append(os.path.expandvars(container['name']))
                    
                    for container in spec['containers']:
                        containers.append(os.path.expandvars(container['name']))

                except KeyError as error:
                    print(error)
                    exit(1)
    return containers