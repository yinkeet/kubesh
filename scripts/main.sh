#!/bin/bash

usage() {
	for i in "${ALL_ENVIRONMENTS[@]}"
	do
		IFS='=' read -ra environment <<< "$i"
		description="${environment[0]}_DESCRIPTION"
		description=${!description}
		string=$(printf '%-13s%s' "${environment[1]}" "$description")
		if [[ ! $environments ]]; then
			environments=$string
		else
			environments="$environments\n  $string"
		fi
	done

	echo ""
	echo "Usage: ./docker-utilities ENVIRONMENT [arg...]"
	echo "       ./docker-utilities HELPERS [arg...]"
    echo "       ./docker-utilities [ -h | --help ]"
	echo ""
	echo "Options:"
	echo "  -h, --help    Prints usage."
	echo ""
    echo "Environment:"
	echo -e "  $environments"
	echo ""
    echo "Helpers:"
    echo "  $DOCKER       Docker helper."
	echo "  $GCLOUD       Kubernetes helper."
	echo "  $KUBERNETES   Kubernetes helper."
	echo ""
	echo "Clipboard:"
	echo "  Starting minikube: minikube start && eval \$(minikube docker-env)"
	echo "  Stopping minikube: minikube stop && eval \$(minikube docker-env -u)"
	echo ""
	exit
}

environment_help() {
    local environment=$1
    echo ""
	echo "Usage: ./docker-utilities $environment COMMANDS"
    echo "       ./docker-utilities [ -h | --help ]"
	echo ""
	echo "Options:"
	echo "  -h, --help    Prints usage."
	echo ""
    echo "Commands:"
	contains $environment ${KUBE_ENVIRONMENTS[@]}
	if [ $? -eq 1 ]; then
		echo "  $SET_CLUSTER      Switch cluster."
	fi
	echo "  $BUILD        Build, tag and push image(s)."
	echo "  $RUN          Run deployment."
    echo "  $STOP         Stop deployment."
    echo "  $SSH          Tunnel into container of the deployment."
    echo "  $LOG          Show logs of container in deployment."
	echo "  $LS           List all containers in deployment."
	echo ""
	exit
}

environment_arguments_parser() {
	# No arguments, show help
	if [ "$#" -eq 0 ]; then
		return 0
	fi

	# Help needed
	if [[ $1 = "-h" ]] || [[ $1 = "--help" ]]; then
		return 0
	fi

	# Commands
	if [[ $1 = $SET_CLUSTER ]] || [[ $1 = $BUILD ]] || [[ $1 = $RUN ]] || [[ $1 = $STOP ]] || [[ $1 = $SSH ]] || [[ $1 = $LOG ]] || [[ $1 = $LS ]]; then
		return 1
	fi
}

dev_commands_exec() {
	local environment=$1
	shift
	if [[ $1 = $BUILD ]]; then
		shift
		build_dev $environment
	elif [[ $1 = $RUN ]]; then
		shift
		run_dev $environment $@
	elif [[ $1 = $STOP ]]; then
		stop_dev $environment
	elif [[ $1 = $SSH ]]; then
		shift
		ssh_dev $environment $@
	elif [[ $1 = $LOG ]]; then
		shift
		log_dev $environment $@
	elif [[ $1 = $LS ]]; then
		shift
		ls_dev $environment $@
	fi
	exit
}

minikube_commands_exec() {
	local environment=$1
	shift
	if [[ $1 = $BUILD ]]; then
		shift
		build_minikube $environment $@
	elif [[ $1 = $RUN ]]; then
		shift
		run_kube $environment $@
	elif [[ $1 = $STOP ]]; then
		stop_kube $environment
	elif [[ $1 = $SSH ]]; then
		shift
		ssh_kube $environment $@
	elif [[ $1 = $LOG ]]; then
		shift
		log_kube $environment $@
	elif [[ $1 = $LS ]]; then
		ls_kube
	fi
	exit
}

kube_commands_exec() {
	local environment=$1
	shift
	if [[ $1 = $SET_CLUSTER ]]; then
		shift
		gcloud container clusters get-credentials $CLUSTER --zone $ZONE --project $PROJECT_NAME
	elif [[ $1 = $BUILD ]]; then
		shift
		build_kube $environment $@
	elif [[ $1 = $RUN ]]; then
		shift
		run_kube $environment $@
	elif [[ $1 = $STOP ]]; then
		stop_kube $environment
	elif [[ $1 = $SSH ]]; then
		shift
		ssh_kube $environment $@
	elif [[ $1 = $LOG ]]; then
		shift
		log_kube $environment $@
	elif [[ $1 = $LS ]]; then
		ls_kube
	fi
	exit
}

contains $1 ${ALL_ENVIRONMENTS[@]}
if [ $? -eq 1 ]; then
	environment=$1
	shift
	environment_arguments_parser $@
	if [ $? -eq 0 ]; then
	 	environment_help $environment
	else
		# Load environment file
		env_file=$(get_config $environment "_ENV" ${ALL_ENVIRONMENTS[@]})
		env_file="$PWD/$env_file"
		if [ ! -f $env_file ]; then
			echo "'$env_file' not found!"
			exit
		fi
		source $env_file
		# Command exec
		# Docker environment
		contains $environment ${DOCKER_ENVIRONMENTS[@]}
		if [ $? -eq 1 ]; then
			dev_commands_exec $environment $@
		fi
		contains $environment ${MINIKUBE_ENVIRONMENTS[@]}
		if [ $? -eq 1 ]; then
			minikube_commands_exec $environment $@
		fi
		contains $environment ${KUBE_ENVIRONMENTS[@]}
		if [ $? -eq 1 ]; then
			kube_commands_exec $environment $@
		fi
	fi
fi