#!/bin/bash

stop_dev() {
	local environment=$1
    shift
	local filename
	filename=$(get_config $environment "_DOCKER_COMPOSE_YML" ${DOCKER_ENVIRONMENTS[@]})
	if [ $? -eq 0 ]; then
		echo "Filename for $environment docker-compose.yml not specified!"
		exit 1
	fi
	echo "Stopping $APP..."
	docker-compose -f "$PWD/$filename" stop
}

stop_kube() {
    local environment=$1
	echo "Stopping $APP..."

	local environments=( "${MINIKUBE_ENVIRONMENTS[@]}" "${KUBE_ENVIRONMENTS[@]}" )
	local filename
	filename=$(get_config $environment "_DEPLOYMENT_YAML" ${environments[@]})
	if [ $? -eq 0 ]; then
		echo "Filename for $environment deployment.yaml not specified!"
		exit 1
	fi

	deployment_file="$PWD/$filename"
	if [ ! -f $deployment_file ]; then
		echo "'$deployment_file' not found!"
		exit
	fi

	local container
	for container in "${CONTAINERS[@]}"
	do
		local image_name=$(generate_image_name $environment $container)
		eval "${container}_image_name=$image_name"
	done

	cat $deployment_file | envsubst | kubectl delete -f -
}