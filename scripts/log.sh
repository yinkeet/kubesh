#!/bin/bash

log_dev_help() {
	local environment=$1
	echo ""
	echo "Usage: ./kubesh $environment log CONTAINER_NAME [OPTION]"
	echo "       ./kubesh $environment log [ -h | --help ]"
    echo ""
	echo "Container name:"
	echo "  Name of container defined in docker-compose.yml"
	echo ""
	echo "Options:"
    echo "  -h, --help    Prints usage."
	echo "  -f, --follow  Tails the log."
	echo ""
	exit
}

log_kube_help() {
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
	echo "Usage: ./kubesh $environment log POD_NAME CONTAINER_NAME [OPTION]"
	echo "       ./kubesh $environment log [ -h | --help ]"
    echo ""
    echo "Pod name:"
	echo -e "  $pods"
	echo ""
	echo "Container name:"
	echo -e "  $containers"
	echo ""
	echo "Options:"
    echo "  -h, --help    Prints usage."
	echo "  -f, --follow  Tails the log."
	echo ""
	exit
}

log_dev_arguments_parser() {
    if [ "$#" -eq 0 ] || [ $1 = "-h" ] || [ $1 = "--help" ]; then
		return 0
	fi

	container_name=$1
	shift

    follow=false
	for i in "$@"
	do
	case $i in
		-h|--help)
		return 0
		;;
		-f|--follow)
		follow=true
		shift # past argument=value
		;;
		*)
		;;
	esac
	done

    args=()
	if [ "$follow" = true ] ; then
		args+=("-f")
	fi
	args+=($container_name)
    echo "${args[*]}"
    return 1
}

log_kube_arguments_parser() {
    if [ "$#" -eq 0 ] || [ $1 = "-h" ] || [ $1 = "--help" ]; then
		return 0
	fi

	pod_name=$1
	shift
	container_name=$1
	shift

    follow=false
	for i in "$@"
	do
	case $i in
		-h|--help)
		return 0
		;;
		-f|--follow)
		follow=true
		shift # past argument=value
		;;
		*)
		;;
	esac
	done

    args="$pod_name -c $container_name"
	if [ "$follow" = true ] ; then
		args="$args -f"
	fi
	
	echo $args
    return 1
}

log_dev() {
	local environment=$1
    shift
    args=$(log_dev_arguments_parser $@)
	if [ $? -eq 0 ]; then
	 	log_dev_help $environment
	else
		echo "Showing $APP logs..."
		local filename
        filename=$(get_config $environment "_DOCKER_COMPOSE_YML" ${DOCKER_ENVIRONMENTS[@]})
        if [ $? -eq 0 ]; then
            echo "Filename for $environment docker-compose.yml not specified!"
            exit 1
        fi
		docker-compose -f "$PWD/$filename" logs $args
	fi
}

log_kube() {
	environment=$1
    shift
	args=$(log_kube_arguments_parser $@)
	if [ $? -eq 0 ]; then
	 	log_kube_help $environment
	else
		kubectl logs $args
	fi
}