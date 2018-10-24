from subprocess import call, check_output, PIPE

from common import load_environment_variables, generate_image_name
from kubernetes import Kubernetes


class AKS(Kubernetes):
    def get_build_image_name(self, container: str) -> str:
        image_name = generate_image_name(container, self.templates['aks_image_name'])
        if not self.production:
            image_name += ':latest'
        else:
            with open(container + '/tag') as tag:
                image_name += ':' + tag.read()
        return image_name

    def get_deployment_image_name(self, container: str) -> str:
        variables = load_environment_variables(['AZURE_CONTAINER_REGISTRY_NAME'])
        acr_name = variables['AZURE_CONTAINER_REGISTRY_NAME']
        short_image_name = generate_image_name(container, self.templates['aks_short_image_name'])
        if not self.production:
            short_image_name += ':latest'
        else:
            with open(container + '/tag') as tag:
                short_image_name += ':' + tag.read()
        digest = check_output(['az', 'acr', 'repository', 'show', '--name', acr_name, '--image', short_image_name, '--query', 'digest', '--output', 'tsv']).decode('UTF-8').replace('\n', '')
        return self.get_build_image_name(container) + '@' + digest

    def container_built_and_pushed(self, container: str) -> bool:
        variables = load_environment_variables(['AZURE_CONTAINER_REGISTRY_NAME'])
        acr_name = variables['AZURE_CONTAINER_REGISTRY_NAME']
        image_name = generate_image_name(container, self.templates['aks_short_image_name'])
        with open(container + '/tag') as tag:
            image_name += ':' + tag.read()
        return call(['az', 'acr', 'repository', 'show', '--name', acr_name, '--image', image_name], stdout=PIPE, stderr=PIPE) == 0