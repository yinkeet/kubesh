from subprocess import PIPE, call, check_output
from typing import List

from library.common import WrapPrint, load_environment_variables
from library.kubernetes import Kubernetes
from library.environment import NameFactory

class AKS(Kubernetes):
    def __init__(self, info: dict, templates: dict):
        super().__init__(info, templates)
        self.image_name_factory = NameFactory(
            self.templates.get('aks_image_name', 'localhost:5000/$NAMESPACE/$APP/__CONTAINER__') + ':latest'
        )
        self.short_image_name_factory = NameFactory(
            self.templates.get('aks_short_image_name', '$NAMESPACE/$APP/__CONTAINER__') + ':latest'
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
        variables = load_environment_variables(['AZURE_CONTAINER_REGISTRY_NAME'])
        image_name = self.short_image_name_factory.make({'__CONTAINER__': container})
        if not self.production:
            image_name += ':latest'
        else:
            with open(container + '/tag') as tag:
                image_name += ':' + tag.read()
        digest = check_output(['az', 'acr', 'repository', 'show', '--name', variables['AZURE_CONTAINER_REGISTRY_NAME'], '--image', image_name, '--query', 'digest', '--output', 'tsv']).decode('UTF-8').replace('\n', '')
        return self.get_build_image_name(container) + '@' + digest

    def container_built_and_pushed(self, container: str) -> bool:
        variables = load_environment_variables(['AZURE_CONTAINER_REGISTRY_NAME'])
        image_name = self.short_image_name_factory.make({'__CONTAINER__': container})
        with open(container + '/tag') as tag:
            image_name += ':' + tag.read()
        return call(['az', 'acr', 'repository', 'show', '--name', variables['AZURE_CONTAINER_REGISTRY_NAME'], '--image', image_name], stdout=PIPE, stderr=PIPE) == 0

    @WrapPrint('Azure doesn\'t support clean ups... ', 'sorry')
    def clean_up(self, containers: List[str]):
        pass

    def auth(self):
        variables = load_environment_variables(['AZURE_APP_ID', 'AZURE_PASSWORD', 'AZURE_TENANT', 'AZURE_CONTAINER_REGISTRY_NAME'])
        self._azure_login(variables['AZURE_APP_ID'], variables['AZURE_PASSWORD'], variables['AZURE_TENANT'])
        self._azure_acr_login(variables['AZURE_CONTAINER_REGISTRY_NAME'])

    @WrapPrint('Logging into azure... ', 'done')
    def _azure_login(self, app_id: str, password: str, tenant: str):
        call(['az', 'login', '--service-principal', '-u', app_id, '-p', password, '--tenant', tenant], stdout=PIPE)

    @WrapPrint('Logging into azure container registry... ', 'done')
    def _azure_acr_login(self, name: str):
        call(['az', 'acr', 'login', '--name', name], stdout=PIPE)

    def cluster(self):
        variables = load_environment_variables(['AZURE_RESOURCE_GROUP', 'CLUSTER'])
        print('Pointing to azure \'' + variables['CLUSTER'] + '\' cluster... ', end='', flush=True)
        call(['az', 'aks', 'get-credentials', '--resource-group', variables['AZURE_RESOURCE_GROUP'], '--name', variables['CLUSTER'], '--overwrite-existing'], stdout=PIPE)
        print('done')
