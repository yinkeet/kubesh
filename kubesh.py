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
from azure import Azure
from common import load_environment_file, load_environment_variables
from docker import Docker
from google import Google
from kubernetes import Kubernetes
from gke import GKE
from minikube import Minikube

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

if args.environment == 'docker':
    method = getattr(Docker, args.operation)()
elif args.environment == 'kubernetes':
    if args.operation == 'image_pull_secret':
        info = settings['environments'][args.name]
        load_environment_file(info['environment_filename'])
        Kubernetes.create_image_pull_secret()
elif args.environment == 'azure' or args.environment == 'google':
    info = settings['environments'][args.name]
    class_map = {
        'azure': Azure,
        'google': Google
    }
    klass = class_map.get(args.environment)
    instance = klass(info)
    method = getattr(instance, args.operation)()
else:
    info = settings['environments'][args.environment]
    load_environment_file(info['environment_filename'])

    # Docker
    if info['type'] == 'docker':
        instance = Docker(info, settings['templates'])
        if args.operation == 'config':
            instance.config()
        elif args.operation == 'logs':
            instance.logs(containers=args.containers, follow=args.follow)
        elif args.operation == 'ssh':
            instance.ssh(container=args.container, command=args.command, args=args.args)
        else:
            getattr(instance, args.operation)(args.containers)

    # Minikube
    elif info['type'] == 'minikube':
        instance = Minikube(info, settings['templates'])
        if args.operation == 'config':
            instance.config()
        elif args.operation == 'logs':
            instance.logs(pod=args.pod, container=args.container, follow=args.follow)
        elif args.operation == 'ssh':
            instance.ssh(pod=args.pod, container=args.container, command=args.command, args=args.args)
        elif args.operation == 'url':
            instance.url()
        else:
            getattr(instance, args.operation)(containers=args.containers)

    elif info['type'] == 'kubernetes':
        variables = load_environment_variables(['CLOUD_SERVICE'])
        cloud_service = variables['CLOUD_SERVICE']
        if cloud_service == 'azure':
            instance = AKS(info, settings['templates'])
        elif cloud_service == 'google':
            instance = GKE(info, settings['templates'])

        if args.operation == 'build':
            instance.build(containers=args.containers)
        elif args.operation == 'config':
            instance.config()
        elif args.operation == 'image_pull_secret':
            instance.image_pull_secret()
        elif args.operation == 'run':
            instance.run(containers=args.containers)
        elif args.operation == 'stop':
            instance.stop(containers=args.containers)
        elif args.operation == 'logs':
            instance.logs(pod=args.pod, container=args.container, follow=args.follow)
        elif args.operation == 'ssh':
            instance.ssh(pod=args.pod, container=args.container, command=args.command, args=args.args)
        elif args.operation == 'url':
            instance.url()
        else:
            getattr(instance, args.operation)(args.containers)