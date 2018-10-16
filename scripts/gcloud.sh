#!/bin/bash

gcloud_help() {
	echo ""
	echo "Usage: ./kubesh $GCLOUD COMMANDS"
    echo "       ./kubesh [ -h | --help ]"
	echo ""
	echo "Options:"
	echo "  -h, --help    Prints usage."
	echo ""
    echo "Commands:"
	echo "  $AUTH         Authenticate using the supplied json file."
	echo "  $CLUSTER_COMMAND      Switch cluster."
	echo ""
	exit
}

gcloud_auth_help() {
	echo ""
	echo "Usage: ./kubesh $GCLOUD $AUTH FILENAME"
    echo "       ./kubesh [ -h | --help ]"
	echo ""
	echo "Options:"
	echo "  -h, --help    Prints usage."
	echo ""
	exit
}

gcloud_cluster_help() {
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
	echo "Usage: ./kubesh $GCLOUD $CLUSTER_COMMAND ENVIRONMENT"
    echo "       ./kubesh [ -h | --help ]"
	echo ""
	echo "Options:"
	echo "  -h, --help    Prints usage."
	echo ""
	echo "Environments:"
	echo -e "  $environments"

	exit
}

gcloud_arguments_parser() {
	# No arguments, show help
	if [ "$#" -eq 0 ]; then
		return 0
	fi

	# Help needed`
	if [[ $1 = "-h" ]] || [[ $1 = "--help" ]]; then
		return 0
	fi

	# Cleanup
	if [[ $1 = $AUTH ]] || [[ $1 = $CLUSTER_COMMAND ]]; then
		return 1
	fi
}

gcloud_auth_arguments_parser() {
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

	return 1
}

gcloud_cluster_arguments_parser() {
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

gcloud_auth() {
	gcloud_auth_arguments_parser $@
    if [ $? -eq 0 ]; then
	 	gcloud_auth_help
    fi

	filename=$1
    auth_key="$PWD/$filename"
    if [ ! -f $auth_key ]; then
        echo "'$auth_key' not found!"
        exit
    fi

    gcloud auth activate-service-account --key-file $auth_key
}

gcloud_cluster() {
	gcloud_cluster_arguments_parser $@
    if [ $? -eq 0 ]; then
	 	gcloud_cluster_help
    fi

	local environment=$1
	load_environment_file $environment
	gcloud container clusters get-credentials $CLUSTER --zone $ZONE --project $PROJECT_NAME
}

if [[ $1 = $GCLOUD ]]; then
	shift
	gcloud_arguments_parser $@
	if [ $? -eq 0 ]; then
	 	gcloud_help
	else
		if [[ $1 = $AUTH ]]; then
			shift
			gcloud_auth $@
			exit
		elif [[ $1 = $CLUSTER_COMMAND ]]; then
			shift
			gcloud_cluster $@
			exit
		fi
	fi
fi