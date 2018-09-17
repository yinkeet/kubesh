#!/bin/bash

docker_help() {
	echo ""
	echo "Usage: ./docker-utilities $DOCKER COMMANDS"
    echo "       ./docker-utilities [ -h | --help ]"
	echo ""
	echo "Options:"
	echo "  -h, --help    Prints usage."
	echo ""
    echo "Commands:"
	echo "  $CLEANUP            Removes stopped containers, followed by untagged images and then unused volumes."
	echo "  $KILL               Forcefully removes all images."
	echo ""
	exit
}

docker_arguments_parser() {
	# No arguments, show help
	if [ "$#" -eq 0 ]; then
		return 0
	fi

	# Help needed`
	if [[ $1 = "-h" ]] || [[ $1 = "--help" ]]; then
		return 0
	fi

	# Cleanup
	if [[ $1 = $CLEANUP ]]; then
		return 1
	fi

	# Kill
	if [[ $1 = $KILL ]]; then
		return 1
	fi
}

if [[ $1 = $DOCKER ]]; then
	shift
	docker_arguments_parser $@
	if [ $? -eq 0 ]; then
	 	docker_help
	else
		if [[ $1 = $CLEANUP ]]; then
			cleanup
			exit
		fi

		if [[ $1 = $KILL ]]; then
			kill_all_images
			exit
		fi
	fi
fi

remove_stopped_containers() {
	containers="$(docker ps -a -f status=exited -q)"
	if [ ${#containers} -gt 0 ]; then
		echo "Removing all stopped containers."
		docker rm $containers
	else
		echo "All stopped containers has already been removed."
	fi
}

remove_all_images() {
	containers="$(docker images -q)"
	if [ ${#containers} -gt 0 ]; then
		echo "Removing all untagged images."
		docker rmi -f $containers
	else
		echo "All untagged images has already been removed."
	fi
}

remove_untagged_images() {
	containers="$(docker images -f "dangling=true" -q)"
	if [ ${#containers} -gt 0 ]; then
		echo "Removing all untagged images."
		docker rmi $containers
	else
		echo "All untagged images has already been removed."
	fi
}

remove_unused_volumes() {
	containers="$(docker volume ls -qf dangling=true)"
	if [ ${#containers} -gt 0 ]; then
		echo "Removing all unused volumes."
		docker volume rm $containers
	else
		echo "All unused volumes has already been removed."
	fi
}

cleanup() {
	echo "Cleaning up docker."
	remove_stopped_containers
	remove_untagged_images
	remove_unused_volumes
}

kill_all_images() {
	echo "Killing all images."
	remove_all_images
}