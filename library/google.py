import os
from subprocess import call
from sys import exit

from cloudservice import CloudService
from common import load_environment_variables

class Google(CloudService):
    def auth(self):
        variables = load_environment_variables(['GOOGLE_AUTH_KEY_FILE'])
        call(['gcloud', 'auth', 'activate-service-account', '--key-file', variables['GOOGLE_AUTH_KEY_FILE']])
        
    def cluster(self):
        variables = load_environment_variables(['CLUSTER', 'ZONE', 'PROJECT'])
        call(['gcloud', 'container', 'clusters', 'get-credentials', variables['CLUSTER'], '--zone', variables['ZONE'], '--project', variables['PROJECT']])
