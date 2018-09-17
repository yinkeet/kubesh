#!/bin/bash

ssh_dev_help() {
	local environment=$1
    echo ""
	echo "Usage: ./docker-utilities $environment ssh CONTAINER_NAME COMMAND"
	echo "       ./docker-utilities $environment ssh [ -h | --help ]"
    echo ""
	echo "Container name:"
	echo "  Name of container defined in docker-compose.yml"
	echo ""
	echo "Command:"
	echo "  bash, sh and etc..."
	echo ""
    echo "Options:"
    echo "  -h, --help    Prints usage."
	echo ""
	exit
}

ssh_kube_help() {
    local environment=$1

    pod_array=($(kubectl get pods -o json | jq '.items[].metadata.name' | grep $APP))
    for i in "${pod_array[@]}"
	do
        i="${i%\"}"
	    i="${i#\"}"
        if [[ ! $pods ]]; then
			pods=$i
		else
			pods="$pods\n  $i"
		fi
	done

	local container
    for container in "${CONTAINERS[@]}"
	do
		if [[ ! $containers ]]; then
			containers="$container"
		else
			containers="$containers\n  $container"
		fi
	done
    
    echo ""
	echo "Usage: ./docker-utilities $environment ssh POD_NAME CONTAINER_NAME COMMAND"
	echo "       ./docker-utilities $environment ssh [ -h | --help ]"
    echo ""
    echo "Pod name:"
	echo -e "  $pods"
	echo ""
	echo "Container name:"
	echo -e "  $containers"
	echo ""
	echo "Command:"
	echo "  bash, sh and etc..."
	echo ""
    echo "Options:"
    echo "  -h, --help    Prints usage."
	echo ""
	exit
}

ssh_dev_arguments_parser() {
    if [ "$#" -lt 2 ]; then
		return 0
	fi

	for i in "$@"
	do
	case $i in
		-h|--help)
		return 0
		;;
	esac
	done

    return 1
}

ssh_kube_arguments_parser() {
    if [ "$#" -lt 3 ] || [ $1 = "-h" ] || [ $1 = "--help" ]; then
		return 0
	fi

    return 1
}

ssh_dev() {
	local environment=$1
    shift
	ssh_dev_arguments_parser $@
	if [ $? -eq 0 ]; then
	 	ssh_dev_help $environment
	else
        echo "Tunneling into $APP..."
		local filename
        filename=$(get_config $environment "_DOCKER_COMPOSE_YML" ${DOCKER_ENVIRONMENTS[@]})
        if [ $? -eq 0 ]; then
            echo "Filename for $environment docker-compose.yml not specified!"
            exit 1
        fi
		docker-compose -f "$PWD/$filename" exec $@
	fi
}

ssh_kube() {
    local environment=$1
    shift
	ssh_kube_arguments_parser $@
	if [ $? -eq 0 ]; then
	 	ssh_kube_help $environment
	else
		pod_name=$1
        shift
        container_name=$1
        shift
        kubectl exec -it $pod_name --container=$container_name -- $@
	fi
}