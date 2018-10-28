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

    @property
    @abstractmethod
    def image_name_template(self) -> str:
        pass
    
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