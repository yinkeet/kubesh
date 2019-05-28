import os
import sys
from subprocess import PIPE, CalledProcessError, call, check_output, run
from time import sleep
from typing import List

from library.common import WrapPrint, load_environment_variables
from library.environment import NameFactory
from library.kubernetes import Kubernetes


class GKE(Kubernetes):
    def __init__(self, info: dict, templates: dict):
        super().__init__(info, templates)
        self.image_name_factory = NameFactory(
            self.templates.get('gcr_image_name', '$CONTAINER_REGISTRY/$PROJECT/$NAMESPACE/$APP/__CONTAINER__')
        )

    def get_build_image_name(self, container: str) -> str:
        image_name = self.image_name_factory.make({'__CONTAINER__': container})
        if not self.production:
            image_name += ':latest'
        else:
            with open(container + '/tag') as tag:
                image_name += ':' + tag.read()
        return image_name

    def get_deployment_image_name(self, container: str) -> str:
        image_name = self.get_build_image_name(container)
        return check_output(['gcloud', 'container', 'images', 'describe', image_name, '--format', 'value(image_summary.fully_qualified_digest)']).decode('UTF-8').replace('\n', '')

    def container_built_and_pushed(self, container: str) -> bool:
        image_name = self.image_name_factory.make({'__CONTAINER__': container})
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

    def clean_up(self, containers: List[str]):
        untagged_images = []
        for container in containers:
            image_name = self.image_name_factory.make({'__CONTAINER__': container})
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
        else:
            print('Nothing to clean')

    def auth(self):
        variables = load_environment_variables(['GOOGLE_AUTH_KEY_FILE', 'CONTAINER_REGISTRY'])
        call(['gcloud', 'auth', 'activate-service-account', '--key-file', variables['GOOGLE_AUTH_KEY_FILE']])
        with open(variables['GOOGLE_AUTH_KEY_FILE']) as text_file:
            keyfile = text_file.read()
        run(['docker', 'login', '-u', '_json_key', '--password-stdin',
             'https://' + variables['CONTAINER_REGISTRY']], input=keyfile, encoding='UTF-8', stdout=PIPE)

    def cluster(self):
        variables = load_environment_variables(['CLUSTER', 'ZONE', 'PROJECT'])
        call(['gcloud', 'container', 'clusters', 'get-credentials', variables['CLUSTER'], '--zone', variables['ZONE'], '--project', variables['PROJECT']])
