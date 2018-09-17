#!/bin/bash

ls_dev() {
	local environment=$1
    shift
    echo "Listing all containers in $APP..."
	local filename
	filename=$(get_config $environment "_DOCKER_COMPOSE_YML" ${DOCKER_ENVIRONMENTS[@]})
	if [ $? -eq 0 ]; then
		echo "Filename for $environment docker-compose.yml not specified!"
		exit 1
	fi
	docker-compose -f "$PWD/$filename" ps $@
}

ls_kube() {
	echo "Listing all pods of $APP..."
	kubectl get pods -o json | jq '.items[].metadata.name' | grep $APP
}