import os
from functools import partial, wraps
from subprocess import CalledProcessError, check_output
from sys import exit

from dotenv import load_dotenv

class Condition(object):
    def __init__(self, kwarg_name, func, *args):
        self.kwarg_name = kwarg_name
        self.func = func
        self.args = args

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            if not kwargs[self.kwarg_name]:
                func_args = [getattr(args[0], arg) for arg in self.args]
                kwargs[self.kwarg_name] = self.func(*func_args)
            return func(*args,**kwargs)
        return wrapper

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

def generate_image_name(container: str, image_name_template: str) -> str:
    template = os.path.expandvars(image_name_template)
    return template.replace('__CONTAINER__', container)

@WrapPrint('Loading deployment file... ', 'done')
def load_deployment_file(deployment_filename: str):
    with open(deployment_filename, 'r') as deployment_file:
        data = deployment_file.read()
    return os.path.expandvars(data)

def minikube_health_checker(func):
    def wrapper(*args, **kwargs):
        try:
            status = check_output(['minikube', 'status', '--format', '{{.MinikubeStatus}}']).decode('UTF-8')
        except CalledProcessError as error:
            status = error.output.decode('UTF-8')
        if status != 'Running':
            print('Minikube is not running, start it by running this command:')
            print('minikube start && eval $(minikube docker-env)')
            exit(1)
        func(*args, **kwargs)
    return wrapper

def get_containers(dockerfile_filename):
    return check_output(
        ['find', '.', '-type', 'f', '-name', dockerfile_filename]
    ).decode('UTF-8').replace('./', '').replace('/' + dockerfile_filename, '').splitlines()