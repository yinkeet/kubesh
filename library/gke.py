import os
import sys
from subprocess import PIPE, CalledProcessError, call, check_output, run
from time import sleep

import requests

from common import load_environment_variables
from kubernetes import Kubernetes


class GKE(Kubernetes):
    def get_build_image_name(self, container: str) -> str:
        image_name = generate_image_name(container, self.templates['gcr_image_name'])
        if not self.production:
            image_name += ':latest'
        else:
            with open(container + '/tag') as tag:
                image_name += ':' + tag.read()
        return image_name

    def get_deployment_image_name(self, container: str) -> str:
        image_name = generate_image_name(container, self.templates['gcr_image_name'])
        if not self.production:
            image_name += ':latest'
        else:
            with open(container + '/tag') as tag:
                image_name += ':' + tag.read()
        digest = check_output(['gcloud', 'container', 'images', 'describe', image_name, '--format="value(image_summary.digest)"']).decode('UTF-8').replace('\n', '')
        return self.get_build_image_name(container) + '@' + digest

    def container_built_and_pushed(self, container: str) -> bool:
        variables = load_environment_variables(['AZURE_CONTAINER_REGISTRY_NAME'])
        acr_name = variables['AZURE_CONTAINER_REGISTRY_NAME']
        image_name = generate_image_name(container, self.templates['aks_short_image_name'])
        with open(container + '/tag') as tag:
            image_name += ':' + tag.read()
        return call(['az', 'acr', 'repository', 'show', '--name', acr_name, '--image', image_name], stdout=PIPE, stderr=PIPE) == 0
