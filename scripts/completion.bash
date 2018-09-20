#/usr/bin/env bash

_completions() {
    HOME_PATH=$(which kubesh | sed -e 's|/kubesh||')

    source "$HOME_PATH/.env"
    if [ -f "kubesh.env" ]; then
        source "kubesh.env"
    fi

    source "$HOME_PATH/scripts/variables.env"
    source "$HOME_PATH/scripts/common.sh"

    if [ "${#COMP_WORDS[@]}" -eq "2" ]; then
        _main_completions
    elif [ "${#COMP_WORDS[@]}" -eq "3" ]; then
        _environments_completions
    fi
}

complete -F _completions kubesh

_main_completions() {
    local all_environments=( "${DOCKER_ENVIRONMENTS[@]}" "${MINIKUBE_ENVIRONMENTS[@]}" "${KUBE_ENVIRONMENTS[@]}" )
    local environment

    local environments=()
    for environment in "${all_environments[@]}"
	do
		IFS='=' read -ra strings <<< "$environment"
        environments+=( ${strings[1]} )
	done

    local helpers=( "$DOCKER $GCLOUD $KUBERNETES" )

    COMPREPLY=($(compgen -W "${environments[*]}" "${COMP_WORDS[1]}"))
    COMPREPLY+=($(compgen -W "${helpers[*]}" "${COMP_WORDS[1]}"))
}

_environments_completions() {
    local args

    contains ${COMP_WORDS[1]} ${DOCKER_ENVIRONMENTS[@]}
    if [ $? -eq 1 ]; then
        args=( "$BUILD $RUN $STOP $SSH $LOG $LS" )
    fi

    contains ${COMP_WORDS[1]} ${MINIKUBE_ENVIRONMENTS[@]}
    if [ $? -eq 1 ]; then
        args=( "$BUILD $RUN $STOP $SSH $LOG $LS $URL" )
    fi

    contains ${COMP_WORDS[1]} ${KUBE_ENVIRONMENTS[@]}
    if [ $? -eq 1 ]; then
        args=( "$SET_CLUSTER $BUILD $RUN $STOP $SSH $LOG $LS $URL" )
    fi

    if [ "${COMP_WORDS[1]}" == "$DOCKER" ]; then
        args=( "$CLEANUP $KILL" )
    fi

    if [ "${COMP_WORDS[1]}" == "$GCLOUD" ]; then
        args=( "$AUTH" )
    fi

    if [ "${COMP_WORDS[1]}" == "$KUBERNETES" ]; then
        args=( "$IMAGE_PULL_SECRET" )
    fi

    COMPREPLY=($(compgen -W "${args[*]}" "${COMP_WORDS[2]}"))
}

_containers_completions()
{
    source containers.sh

    args=()
    for i in "${CONTAINERS[@]}"
    do
        IFS='=' read -ra container <<< "$i"
        args+=("${container[1]}")
    done

    COMPREPLY=($(compgen -W "${args[*]}" "${COMP_WORDS[2]}"))
}