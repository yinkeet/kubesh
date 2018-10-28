from subprocess import call, check_output, PIPE

from common import load_environment_variables, generate_image_name, WrapPrint
from kubernetes import Kubernetes


class AKS(Kubernetes):
    @property
    def image_name_template(self) -> str:
        return self.templates.get('aks_image_name', '$CONTAINER_REGISTRY/$APP/__CONTAINER__')

    @property
    def short_image_name_template(self) -> str:
        return self.templates.get('aks_short_image_name', '$APP/__CONTAINER__')

    def get_build_image_name(self, container: str) -> str:
        image_name = generate_image_name(container, self.image_name_template)
        if not self.production:
            image_name += ':latest'
        else:
            with open(container + '/tag') as tag:
                image_name += ':' + tag.read()
        return image_name

    def get_deployment_image_name(self, container: str) -> str:
        variables = load_environment_variables(['AZURE_CONTAINER_REGISTRY_NAME'])
        acr_name = variables['AZURE_CONTAINER_REGISTRY_NAME']
        short_image_name = generate_image_name(container, self.short_image_name_template)
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
        image_name = generate_image_name(container, self.short_image_name_template)
        with open(container + '/tag') as tag:
            image_name += ':' + tag.read()
        return call(['az', 'acr', 'repository', 'show', '--name', acr_name, '--image', image_name], stdout=PIPE, stderr=PIPE) == 0

    def auth(self):
        variables = load_environment_variables(['AZURE_APP_ID', 'AZURE_PASSWORD', 'AZURE_TENANT', 'AZURE_CONTAINER_REGISTRY_NAME'])
        self._azure_login(variables['AZURE_APP_ID'], variables['AZURE_PASSWORD'], variables['AZURE_TENANT'])
        self._azure_acr_login(variables['AZURE_CONTAINER_REGISTRY_NAME'])

    @WrapPrint('Logging in azure... ', 'done')
    def _azure_login(self, app_id: str, password: str, tenant: str):
        call(['az', 'login', '--service-principal', '-u', app_id, '-p', password, '--tenant', tenant], stdout=PIPE)

    @WrapPrint('Logging in azure container registry... ', 'done')
    def _azure_acr_login(self, name: str):
        call(['az', 'acr', 'login', '--name', name], stdout=PIPE)

    def cluster(self):
        variables = load_environment_variables(['AZURE_RESOURCE_GROUP', 'CLUSTER'])
        print('Pointing to azure \'' + variables['CLUSTER'] + '\' cluster... ', end='', flush=True)
        call(['az', 'aks', 'get-credentials', '--resource-group', variables['AZURE_RESOURCE_GROUP'], '--name', variables['CLUSTER'], '--overwrite-existing'], stdout=PIPE)
        print('done')