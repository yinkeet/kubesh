import os
import sys
from subprocess import PIPE, CalledProcessError, call, check_output, run
from time import sleep
from typing import List

from common import (Condition, WrapPrint, generate_image_name, get_containers,
                    load_environment_variables)
from kubernetes import Kubernetes


class GKE(Kubernetes):
    @property
    def image_name_template(self) -> str:
        if self.templates is None:
            return '$CONTAINER_REGISTRY/$PROJECT/$NAMESPACE/$APP/__CONTAINER__'
        else:
            return self.templates.get('gcr_image_name', '$CONTAINER_REGISTRY/$PROJECT/$NAMESPACE/$APP/__CONTAINER__')

    def get_build_image_name(self, container: str) -> str:
        image_name = generate_image_name(container, self.image_name_template)
        if not self.production:
            image_name += ':latest'
        else:
            with open(container + '/tag') as tag:
                image_name += ':' + tag.read()
        return image_name

    def get_deployment_image_name(self, container: str) -> str:
        image_name = generate_image_name(container, self.image_name_template)
        if not self.production:
            image_name += ':latest'
        else:
            with open(container + '/tag') as tag:
                image_name += ':' + tag.read()
        return check_output(['gcloud', 'container', 'images', 'describe', image_name, '--format="value(image_summary.fully_qualified_digest)"']).decode('UTF-8').replace('\n', '')

    def container_built_and_pushed(self, container: str) -> bool:
        image_name = generate_image_name(container, self.image_name_template)
        with open(container + '/tag') as tag:
            image_name += ':' + tag.read()
        return call(['gcloud', 'container', 'images', 'describe', image_name], stdout=PIPE, stderr=PIPE) == 0

    @WrapPrint('Creating image pull secret... ', 'done')
    def image_pull_secret(self):
        variables = load_environment_variables([
            'IMAGE_PULL_SECRET_NAME', 'IMAGE_PULL_SECRET_SERVER', 'IMAGE_PULL_SECRET_USERNAME', 'IMAGE_PULL_SECRET_PASSWORD', 'IMAGE_PULL_SECRET_EMAIL'
        ])
        name = variables['IMAGE_PULL_SECRET_NAME']
        server = variables['IMAGE_PULL_SECRET_SERVER']
        username = variables['IMAGE_PULL_SECRET_USERNAME']
        with open(variables['IMAGE_PULL_SECRET_PASSWORD']) as text_file:
            password = text_file.read()
        email = variables['IMAGE_PULL_SECRET_EMAIL']
        data = check_output(['kubectl', 'create', 'secret', 'docker-registry', name, '--docker-server', server, '--docker-username', username, '--docker-password', password, '--docker-email', email, '--dry-run', '-o', 'yaml']).decode('UTF-8')
        run(['kubectl', 'apply', '-f', '-'], input=data, encoding='UTF-8', stdout=PIPE)

    @WrapPrint('Cleaning up... ', 'done')
    @Condition('containers', get_containers, 'dockerfile_filename')
    def clean_up(self, containers: List[str]=[]):
        untagged_images = []
        for container in containers:
            image_name = generate_image_name(container, self.image_name_template)
            digests = check_output(
                ['gcloud', 'container', 'images', 'list-tags', image_name, '--filter=-tags:*', '--limit=unlimited', '--format=get(digest)']
            ).decode('UTF-8').splitlines()
            untagged_images.extend(
                [image_name + '@' + digest for digest in digests]
            )
            
        if untagged_images:
            for untagged_image in untagged_images:
                command = ['gcloud', 'container', 'images', 'delete', '--quiet', untagged_image]
                call(command, stdout=PIPE)

    def auth(self):
        variables = load_environment_variables(['GOOGLE_AUTH_KEY_FILE'])
        call(['gcloud', 'auth', 'activate-service-account', '--key-file', variables['GOOGLE_AUTH_KEY_FILE']])
        call(['docker-credential-gcr', 'configure-docker'])

    def cluster(self):
        variables = load_environment_variables(['CLUSTER', 'ZONE', 'PROJECT'])
        call(['gcloud', 'container', 'clusters', 'get-credentials', variables['CLUSTER'], '--zone', variables['ZONE'], '--project', variables['PROJECT']])
