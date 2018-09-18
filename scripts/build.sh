#!/bin/bash

build_kube_help() {
    local environment=$1

	local container
	local containers
    for container in "${CONTAINERS[@]}"
	do
		if [[ ! $containers ]]; then
			containers=$container
		else
			containers="$containers\n  $container"
		fi
	done

    echo ""
	echo "Usage: ./docker-utilities $environment build [CONTAINER_NAME]"
	echo "       ./docker-utilities $environment build [ -h | --help ]"
	echo ""
	echo "If no CONTAINER_NAME is given then all containers will be built."
    echo ""
	echo "Containers:"
	echo -e "  $containers"
	echo ""
    echo "Options:"
    echo "  -h, --help    Prints usage."
	echo ""
	exit
}

build_kube_arguments_parser() {
	if [ "$#" -eq 0 ]; then
		return 1
	fi

	local argument
	for argument in "$@"
	do
	case $argument in
		-h|--help)
		return 0
		;;
	esac
	done

	local container
	for container in "${CONTAINERS[@]}"
	do
		if [[ $1 = $container ]]; then
			return 2
		fi
	done
	return 0
}

build_dev() {
	echo "Building for $APP..."
    local environment=$1
	local filename
    filename=$(get_config $environment "_DOCKER_COMPOSE_YML" ${DOCKER_ENVIRONMENTS[@]})
    if [ $? -eq 0 ]; then
        echo "Filename for $environment docker-compose.yml not specified!"
        exit
    fi
	docker-compose -f $filename build --force-rm
}

build_minikube_image() {
    local environment=$1
    local container=$2

	local dockerfile
    dockerfile=$(get_config $environment "_DOCKERFILE" ${MINIKUBE_ENVIRONMENTS[@]})
    if [ $? -eq 0 ]; then
        echo "Dockerfile filename for $environment not specified!"
        exit
    fi

    dockerfile="$PWD/$container/$dockerfile"
    if [ ! -f $dockerfile ]; then
        echo "'$dockerfile' not found!"
        exit
    fi

	local image_name=$(generate_image_name $environment $container)
	local tag=$(cat $PWD/$container/tag)
	local image_name_tag="$image_name:$tag"
	docker build --force-rm --no-cache --rm --file $dockerfile -t $image_name_tag $PWD
}

build_image_checker() {
	local image_name=$1
	local tag=$2
	local image_details=$(gcloud container images list-tags $image_name --format=json --filter="tags=$tag" | jq '.[0].tags[0]')
	image_details="${image_details%\"}"
	image_details="${image_details#\"}"
	if [ "$image_details" == "$tag" ]; then
		return 1
	else
		return 0
	fi
}

build_kube_image() {
    local environment=$1
    local container=$2
    
	local image_name=$(generate_image_name $environment $container)
	local tag=$(cat $PWD/$container/tag)
	local image_name_tag="$image_name:$tag"
    
	build_image_checker $image_name $tag
    if [ $? -eq 1 ]; then
        echo "Image $image_name_tag is already built and pushed to the cloud."
    else
        dockerfile=$(get_config $environment "_DOCKERFILE" ${KUBE_ENVIRONMENTS[@]})
        if [ $? -eq 0 ]; then
            echo "Dockerfile filename for $environment not specified!"
            exit
        fi

        dockerfile="$PWD/$container/$dockerfile"
        if [ ! -f $dockerfile ]; then
            echo "'$dockerfile' not found!"
            exit
        fi

        docker build --force-rm --no-cache --rm -f $dockerfile -t $image_name_tag $PWD
	    docker push $image_name_tag
    fi
}

build_kube() {
    local environment=$1
    shift
	build_kube_arguments_parser $@
	if [ $? -eq 0 ]; then
	 	build_kube_help $environment
	elif [ $? -eq 1 ]; then
		echo "Building all images for $APP..."
		local container

		contains $environment ${MINIKUBE_ENVIRONMENTS[@]}
		if [ $? -eq 1 ]; then
			for container in "${CONTAINERS[@]}"
			do
				build_minikube_image $environment $container
			done
			exit
		fi

		contains $environment ${KUBE_ENVIRONMENTS[@]}
		if [ $? -eq 1 ]; then
			for container in "${CONTAINERS[@]}"
			do
				build_kube_image $environment $container
			done
			exit
		fi
	else
		echo "Build and push $1 image for $APP..."
		contains $environment ${MINIKUBE_ENVIRONMENTS[@]}
		if [ $? -eq 1 ]; then
			build_minikube_image $environment $1
			exit
		fi

		contains $environment ${KUBE_ENVIRONMENTS[@]}
		if [ $? -eq 1 ]; then
			build_kube_image $environment $1
			exit
		fi
	fi
}