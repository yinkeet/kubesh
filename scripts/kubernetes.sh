#!/bin/bash

kubernetes_help() {
	echo ""
	echo "Usage: ./kubesh $KUBERNETES COMMANDS"
    echo "       ./kubesh [ -h | --help ]"
	echo ""
	echo "Options:"
	echo "  -h, --help    Prints usage."
	echo ""
    echo "Commands:"
	echo "  $IMAGE_PULL_SECRET  Creates an image pull secret and patches it to service account."
	echo ""
	exit
}

kubernetes_image_pull_secret_help() {
	echo ""
	echo "Usage: ./kubesh $KUBERNETES $IMAGE_PULL_SECRET FILENAME"
    echo "       ./kubesh [ -h | --help ]"
	echo ""
	echo "Options:"
	echo "  -h, --help    Prints usage."
	echo ""
	exit
}

kubernetes_arguments_parser() {
	# No arguments, show help
	if [ "$#" -eq 0 ]; then
		return 0
	fi

	# Help needed
	if [[ $1 = "-h" ]] || [[ $1 = "--help" ]]; then
		return 0
	fi

	# Cleanup
	if [[ $1 = $IMAGE_PULL_SECRET ]]; then
		return 1
	fi
}

kubernetes_image_pull_secret_arguments_parser() {
	# No arguments, show help
	if [ "$#" -eq 0 ]; then
		return 0
	fi

    for i in "$@"
	do
	case $i in
		-h|--help)
		return 0
		;;
		*)
		;;
	esac
	done

	return 1
}

image_pull_secret() {
	kubernetes_image_pull_secret_arguments_parser $@
    if [ $? -eq 0 ]; then
	 	kubernetes_image_pull_secret_help
    fi
    
    local filename=$1
    local image_pull_secret_key="$PWD/$filename"
    if [ ! -f $image_pull_secret_key ]; then
        echo "'$image_pull_secret_key' not found!"
        exit
    fi
    
    # # Load image_pull_secret.yaml
    # local image_pull_secret_yaml="$PWD/image_pull_secret.yaml"
    # if [ ! -f $image_pull_secret_yaml ]; then
    #     image_pull_secret_yaml="$HOME_DIR/image_pull_secret.yaml"
    # fi

    # # Load service_account.yaml
    # local service_account_yaml="$PWD/service_account.yaml"
    # if [ ! -f $service_account_yaml ]; then
    #     service_account_yaml="$HOME_DIR/service_account.yaml"
    # fi

    # # local BASE64_ENCODED_IMAGE_PULL_SECRET_JSON=$(base64 $image_pull_secret_key)
	# local BASE64_ENCODED_IMAGE_PULL_SECRET_JSON=$1
	# envsubst < $image_pull_secret_yaml | kubectl replace -f -
	# cat $service_account_yaml | kubectl replace -f -
	secretName="gcr-json-key"
    metadataName=$(kubectl get secret $secretName -o json | jq '.metadata.name')
    metadataName="${metadataName%\"}"
	metadataName="${metadataName#\"}"
    if [ "$metadataName" == "$secretName" ]; then
        kubectl delete secret $secretName
    fi
    password="$(cat $image_pull_secret_key)"
    kubectl create secret docker-registry gcr-json-key --docker-server=https://gcr.io --docker-username=_json_key --docker-password="$password" --docker-email=tech@imoney-group.com
    kubectl delete serviceaccount default 
    kubectl patch serviceaccount default -p "{\"imagePullSecrets\":[{\"name\":\"$secretName\"}]}"
}

if [[ $1 = $KUBERNETES ]]; then
	shift
	kubernetes_arguments_parser $@
	if [ $? -eq 0 ]; then
	 	kubernetes_help
	else
		if [[ $1 = $IMAGE_PULL_SECRET ]]; then
			shift
			image_pull_secret $@
			exit
		fi
	fi
fi