import os
from abc import ABC, abstractmethod
from typing import List

class Environment(ABC):
    def __init__(self, info: dict, templates: dict):
        super().__init__()
        self.deployment_filename = info['deployment_filename']
        self.dockerfile_filename = info['dockerfile_filename']
        self.production = info['production']
        self.templates = templates

    @abstractmethod
    def build(self, containers: List[str]=[]):
        pass
    
    @abstractmethod
    def config(self):
        pass

    @abstractmethod
    def run(self, containers: List[str]=[]):
        pass

    @abstractmethod
    def clean_up(self, containers: List[str]=[]):
        pass

    @abstractmethod
    def stop(self, containers: List[str]=[]):
        pass

    @abstractmethod
    def logs(self, containers: List[str]=[], pod: str=None, container: str=None, follow: bool=False):
        pass

    @abstractmethod
    def ssh(self, pod: str=None, container: str=None, command: str=None, args: List[str]=[]):
        pass

class NameFactory(object):
    def __init__(self, template: str):
        self.template = template
    
    def make(self, map: dict):
        name = os.path.expandvars(self.template)
        for k, v in map.items():
            name = name.replace(k, v)
        return name