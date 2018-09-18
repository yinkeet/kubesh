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
	if [[ $1 = $AUTH ]]; then
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

auth() {
	shift
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

if [[ $1 = $GCLOUD ]]; then
	shift
	gcloud_arguments_parser $@
	if [ $? -eq 0 ]; then
	 	gcloud_help
	else
		if [[ $1 = $AUTH ]]; then
			auth $@
			exit
		fi
	fi
fi