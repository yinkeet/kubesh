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

azure_auth_help() {
	echo ""
	echo "Usage: ./kubesh $AZURE $AUTH APP_ID PASSWORD TENANT"
    echo "       ./kubesh [ -h | --help ]"
	echo ""
	echo "Options:"
	echo "  -h, --help    Prints usage."
	echo ""
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
    az login --service-principal -u $appId -p $password --tenant $tenant
    az acr login --name $ACR_NAME
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
		fi
	fi
fi