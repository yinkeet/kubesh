#!/bin/bash

azure_help() {
	echo ""
	echo "Usage: ./kubesh $AZURE COMMANDS"
    echo "       ./kubesh [ -h | --help ]"
	echo ""
	echo "Options:"
	echo "  -h, --help    Prints usage."
	echo ""
    echo "Commands:"
	echo "  $AUTH         Authenticate using the appId, password and tenant."
	echo ""
	exit
}

azure_cluster_help() {
	local string
	local array
	local environments
	for string in "${KUBE_ENVIRONMENTS[@]}"
	do
		IFS='=' read -ra array <<< "$string"
		local description="${array[0]}_DESCRIPTION"
		description=${!description}
		string=$(printf '%-13s%s' "${array[1]}" "$description")
		if [[ ! $environments ]]; then
			environments=$string
		else
			environments="$environments\n  $string"
		fi
	done

	echo ""
	echo "Usage: ./kubesh $AZURE $CLUSTER_COMMAND ENVIRONMENT"
    echo "       ./kubesh [ -h | --help ]"
	echo ""
	echo "Options:"
	echo "  -h, --help    Prints usage."
	echo ""
	echo "Environments:"
	echo -e "  $environments"

	exit
}

azure_arguments_parser() {
	# No arguments, show help
	if [ "$#" -eq 0 ]; then
		return 0
	fi

	# Help needed`
	if [[ $1 = "-h" ]] || [[ $1 = "--help" ]]; then
		return 0
	fi

	if [[ $1 = $AUTH ]]; then
		return 1
	fi
}

azure_auth_arguments_parser() {
	# No arguments, show help
	if [ "$#" -eq 0 ]; then
		return 0
	fi

    # Find options
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

    if [[ ! $ACR_NAME ]]; then
        return 0
    fi

	return 1
}

azure_cluster_arguments_parser() {
	# No arguments, show help
	if [ "$#" -eq 0 ]; then
		return 0
	fi

	# Find options
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

	contains $1 ${KUBE_ENVIRONMENTS[@]}
	return $?
}

azure_auth() {
    local found_error=false
    if [[ ! $AZURE_APP_ID ]]; then
        found_error=true
        echo "AZURE_APP_ID not set!"
    fi
    if [[ ! $AZURE_PASSWORD ]]; then
        found_error=true
        echo "AZURE_PASSWORD not set!"
    fi
    if [[ ! $AZURE_TENANT ]]; then
        found_error=true
        echo "AZURE_TENANT not set!"
    fi
	if [[ ! $ACR_NAME ]]; then
        found_error=true
        echo "ACR_NAME not set!"
    fi
    if [ "$found_error" = true ] ; then
        exit 1
    fi
    az login --service-principal -u $AZURE_APP_ID -p $AZURE_PASSWORD --tenant $AZURE_TENANT
    az acr login --name $ACR_NAME
}

azure_cluster() {
	azure_cluster_arguments_parser $@
    if [ $? -eq 0 ]; then
	 	azure_cluster_help
    fi

	local environment=$1
	load_environment_file $environment
    az aks get-credentials --resource-group $AZURE_RESOURCE_GROUP --name $CLUSTER --overwrite-existing
}

azure_container_registry_url() {
    az acr list --resource-group $ACR_NAME --query "[0].loginServer" --output tsv
}

if [[ $1 = $AZURE ]]; then
	shift
	azure_arguments_parser $@
	if [ $? -eq 0 ]; then
	 	azure_help
	else
		if [[ $1 = $AUTH ]]; then
            shift
			azure_auth
			exit
		elif [[ $1 = $CLUSTER_COMMAND ]]; then
			shift
			azure_cluster $@
			exit
		fi
	fi
fi