#! /usr/bin/env python3

import json
import os
import sys
from argparse import ArgumentParser
from pathlib import Path

# dir_path = os.path.dirname(os.path.realpath(__file__)) + '/'
# sys.path.append(dir_path + 'library')

from library.argparser import KubeshArgumentParser
from library.aks import AKS
from library.common import get_containers_from_yaml, load_environment_file, load_environment_variables
from library.docker import Docker
from library.kubernetes import Kubernetes
from library.gke import GKE
from library.minikube import Minikube
from library.environment import Environment
from library.config import Config

parser = KubeshArgumentParser(Config().settings)
args = parser.run()

Config().environment = args.environment

class_map = {
    'docker': Docker,
    'minikube': Minikube,
    'kubernetes': {
        'azure': AKS,
        'google': GKE
    }
}

klass = class_map[Config().current_setting['type']]
if isinstance(klass, dict):
    klass = klass[Config().current_setting['cloud_service']]
instance = klass(Config().current_setting, Config().settings.get('templates', {}))
method = getattr(instance, args.operation)
kwargs = vars(args)
kwargs.pop('environment', None)
kwargs.pop('operation', None)
method(**kwargs)