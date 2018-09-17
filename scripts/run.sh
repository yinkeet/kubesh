#!/bin/bash

run_help() {
    environment=$1
	echo ""
	echo "Usage: ./docker-utilities $environment run [OPTIONS]"
	echo "       ./docker-utilities $environment run [ -h | --help ]"
    echo ""
	echo "Options:"
    echo "  -h, --help    Prints usage."
    echo "  -d, --debug   Prints the deployment file."
	echo ""
	exit
}

run_arguments_parser() {
    # No arguments
    if [ "$#" -eq 0 ]; then
		return 2
	fi

    for i in "$@"
	do
	case $i in
		-h|--help)
		return 0
		;;
		-d|--debug)
		return 1
		;;
	esac
	done

    echo "Error: Invalid option"
	return 0
}

run_dev() {
    local environment=$1
    shift
	run_arguments_parser $@
    local result=$?
	if [ $result -eq 0 ]; then
		run_help $environment
    else
        local filename
        filename=$(get_config $environment "_DOCKER_COMPOSE_YML" ${DOCKER_ENVIRONMENTS[@]})
        if [ $? -eq 0 ]; then
            echo "Filename for $environment docker-compose.yml not specified!"
            exit 1
        fi
        if [ $result -eq 1 ]; then
            echo "Debugging $APP..."
            echo ''
            docker-compose -f "$PWD/$filename" config
            echo ''
        else
            echo "Running $APP..."
		    docker-compose -f "$PWD/$filename" up -d
        fi
    fi
}

run_kube() {
    local environment=$1
    shift
	run_arguments_parser $@
	local result=$?
	if [ $result -eq 0 ]; then
		run_help $environment
    else
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
        
        if [ $result -eq 1 ]; then
            echo "Debugging $APP..."
            echo ''
            cat $deployment_file | envsubst
            echo ''
        else
            echo "Running $APP..."
            cat $deployment_file | envsubst | kubectl apply -f -
        fi
    fi
}