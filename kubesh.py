#! /usr/bin/env python3

import json
import os
import sys
from argparse import ArgumentParser
from pathlib import Path

dir_path = os.path.dirname(os.path.realpath(__file__)) + '/'
sys.path.append(dir_path + 'library')

from argparser import KubeshArgumentParser
from aks import AKS
from common import load_environment_file, load_environment_variables
from docker import Docker
from kubernetes import Kubernetes
from gke import GKE
from minikube import Minikube
from environment import Environment

custom_settings_file = Path("kubesh.json")
if custom_settings_file.is_file():
    with open('kubesh.json') as data:
        settings = json.load(data)
else:
    if getattr(sys, 'frozen', False):
        dir_path = os.path.dirname(os.path.realpath(sys.executable)) + '/'
    with open(dir_path + 'kubesh.json') as data:
        settings = json.load(data)

parser = KubeshArgumentParser(settings)
args = parser.run()

info = settings['environments'][args.environment]
load_environment_file(info['environment_filename'])

class_map = {
    'docker': Docker,
    'minikube': Minikube,
    'kubernetes': {
        'azure': AKS,
        'google': GKE
    }
}

klass = class_map[info['type']]
if isinstance(klass, dict):
    klass = klass[info['cloud_service']]
instance = klass(info, settings['templates'])
method = getattr(instance, args.operation)
kwargs = vars(args)
kwargs.pop('environment', None)
kwargs.pop('operation', None)
method(**kwargs)