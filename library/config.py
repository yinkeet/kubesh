import json
import os
import sys
import yaml
from pathlib import Path
from subprocess import check_output

from library.common import load_environment_file

class Config(object):
    __instance = None
    def __new__(cls):
        if Config.__instance is None:
            Config.__instance = object.__new__(cls)
            Config.__instance.__load_kubesh_json()
            Config.__instance.__load_containers()
        return Config.__instance

    @property
    def environment(self):
        return self._environment

    @environment.setter
    def environment(self, value: str):
        self._environment = value
        load_environment_file(self.current_setting['environment_filename'])

    @property
    def current_setting(self):
        return self.settings['environments'][self.environment]

    def __load_kubesh_json(self):
        if Path("kubesh.json").is_file():
            with open('kubesh.json') as data:
                self.settings = json.load(data)
        else:
            if getattr(sys, 'frozen', False):
                dir_path = os.path.dirname(os.path.realpath(sys.executable)) + '/'
            else:
                dir_path = os.path.dirname(os.path.realpath(__file__)) + '/'
            with open(dir_path + 'kubesh.json') as data:
                self.settings = json.load(data)

    def __load_containers(self):
        for id, setting in dict(self.settings['environments']).items():
            if os.path.isfile(os.getcwd() + '/' + setting['environment_filename']):    
                load_environment_file(setting['environment_filename'])
                if setting['type'] == 'docker':
                    all_containers = self.__get_docker_compose_containers(setting['deployment_filename'])
                else:
                    all_containers = self.__get_deployment_containers(setting['deployment_filename'])
                buildable_containers = self.__filter_buildable_containers(all_containers, setting['dockerfile_filename'])
                self.settings['environments'][id]['containers'] = {
                    'all': all_containers,
                    'buildable': buildable_containers
                }
            else:
                print('Error \'{}\' not found!'.format(setting['environment_filename']))
                del self.settings['environments'][id]

    def __get_docker_compose_containers(self, filenames: str):
        def get_services(filename: str):
            with open(filename, 'r') as stream:
                try:
                    return [service for service, _ in yaml.load(stream)['services'].items()]
                except yaml.YAMLError as error:
                    print(error)
                    exit(1)

        if isinstance(filenames, str):
            return get_services(filenames)
        elif isinstance(filenames, list) and filenames:
            containers = []
            for filename in filenames:
                for container in get_services(filename):
                    if container not in containers:
                        containers.append(container)
            return containers
        else:
            raise ValueError('filenames should be str or list')

    def __get_deployment_containers(self, deployment_filename: str):
        def default_ctor(loader, tag_suffix, node):
            return node.value
        
        containers = []
        with open(deployment_filename, 'r') as stream:
            string = stream.read()
            string = os.path.expandvars(string)
            yaml.add_multi_constructor('', default_ctor)
            for data in yaml.load_all(string):
                if 'kind' in data:
                    if data['kind'] == 'Deployment':
                        try:
                            spec = data['spec']['template']['spec']
                            if 'initContainers' in spec:
                                for container in spec['initContainers']:
                                    containers.append(container['name'])
                            
                            for container in spec['containers']:
                                containers.append(container['name'])
                        except KeyError as error:
                            print(error)
                            exit(1)
                    elif data['kind'] == 'CronJob':
                        try:
                            spec = data['spec']['jobTemplate']['spec']['template']['spec']
                            for container in spec['containers']:
                                containers.append(container['name'])
                        except KeyError as error:
                            print(error)
                            exit(1)
        return containers
        
    def __filter_buildable_containers(self, all_containers: list, dockerfile_filename: str):
        containers = []
        for container in all_containers:
            containers.extend(
                check_output(
                    ['find', '.', '-type', 'f', '-path', './' + container + '/*', '-maxdepth', '2', '-mindepth' ,'2', '-name', dockerfile_filename]
                ).decode('UTF-8').replace('./', '').replace('/' + dockerfile_filename, '').splitlines()
            )
        return containers