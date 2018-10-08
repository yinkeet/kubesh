#!/bin/bash

contains() {
	local target=$1
	shift
	local strings
	for i in $@
	do
		IFS='=' read -ra strings <<< "$i"
		if [[ $target = "${strings[1]}" ]]; then
			return 1
		fi
	done
	return 0
}

get_config() {
    local target=$1
	shift
	local suffix=$1
    shift
	local strings
	for i in $@
	do
		IFS='=' read -ra strings <<< "$i"
		if [[ $target = "${strings[1]}" ]]; then
            local result="${strings[0]}$suffix"
		    result=${!result}
            echo $result
            return 1
        fi
	done
    return 0
}

generate_image_name() {
	local environment=$1
	local container=$2
	
	contains $environment ${MINIKUBE_ENVIRONMENTS[@]}
	if [ $? -eq 1 ]; then
		echo $MINIKUBE_IMAGE_NAME_FORMAT | envsubst
	fi

	contains $environment ${KUBE_ENVIRONMENTS[@]}
	if [ $? -eq 1 ]; then
		echo $KUBE_IMAGE_NAME_FORMAT | envsubst
	fi
}

load_containers() {
	local environment=$1
	local filename
	filename=$(get_config $environment "_DOCKERFILE" ${ALL_ENVIRONMENTS[@]})
	if [ $? -eq 0 ]; then
		echo "Filename for $environment dockerfile not specified!"
		exit
	fi
	CONTAINERS=($(eval "find . -type f -name '$filename' | sed -E 's|/[^/]+$||' | sort -u | sed -e 's/^.\///'"))
}