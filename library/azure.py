from subprocess import PIPE, call

from cloudservice import CloudService
from common import load_environment_variables


class Azure(CloudService):
    def auth(self):
        variables = load_environment_variables(['AZURE_APP_ID', 'AZURE_PASSWORD', 'AZURE_TENANT', 'AZURE_CONTAINER_REGISTRY_NAME'])
        print('Logging in azure... ', end='', flush=True)
        call(['az', 'login', '--service-principal', '-u', variables['AZURE_APP_ID'], '-p', variables['AZURE_PASSWORD'], '--tenant', variables['AZURE_TENANT']], stdout=PIPE)
        print('done')
        print('Logging in azure container registry... ', end='', flush=True)
        call(['az', 'acr', 'login', '--name', variables['AZURE_CONTAINER_REGISTRY_NAME']], stdout=PIPE)
        print('done')
        
    def cluster(self):
        variables = load_environment_variables(['AZURE_RESOURCE_GROUP', 'CLUSTER'])
        print('Pointing to azure \'' + variables['CLUSTER'] + '\' cluster... ', end='', flush=True)
        call(['az', 'aks', 'get-credentials', '--resource-group', variables['AZURE_RESOURCE_GROUP'], '--name', variables['CLUSTER'], '--overwrite-existing'], stdout=PIPE)
        print('done')