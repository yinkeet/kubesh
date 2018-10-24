import os
import sys
from abc import ABC, abstractmethod

from dotenv import load_dotenv

from common import load_environment_file

class CloudService(ABC):
    def __init__(self, info):
        super().__init__()
        load_environment_file(info['environment_filename'])

    @abstractmethod
    def auth(self):
        pass
        
    @abstractmethod
    def cluster(self):
        pass
