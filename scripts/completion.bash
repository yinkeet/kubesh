#/usr/bin/env bash

_completions() {
    HOME_PATH=$(which kubesh | sed -e 's|/kubesh||')

    source "$HOME_PATH/.env"
    if [ -f "kubesh.env" ]; then
        source "kubesh.env"
    fi

    # Merge docker, minikube abd kube environments into one
    MINIKUBE_AND_KUBE_ENVIRONMENTS=( "${MINIKUBE_ENVIRONMENTS[@]}" "${KUBE_ENVIRONMENTS[@]}" )
    ALL_ENVIRONMENTS=( "${DOCKER_ENVIRONMENTS[@]}" "${MINIKUBE_AND_KUBE_ENVIRONMENTS[@]}" )
    # Evaluate all environments
    for i in "${ALL_ENVIRONMENTS[@]}"
    do
        eval $i
    done

    source "$HOME_PATH/scripts/variables.env"
    source "$HOME_PATH/scripts/common.sh"

    if [ "${#COMP_WORDS[@]}" -eq "2" ]; then
        _main_completions
    elif [ "${#COMP_WORDS[@]}" -eq "3" ]; then
        _environments_completions
    elif [ "${#COMP_WORDS[@]}" -eq "4" ]; then
        if [ "${COMP_WORDS[2]}" == "$BUILD" ]; then
            _build_completions
        # elif [ "${COMP_WORDS[2]}" == "$SSH" ]; then

        elif [ "${COMP_WORDS[2]}" == "$LOG" ]; then
            _log_completions
        fi
    fi
}

complete -F _completions kubesh

_main_completions() {
    local environment

    local environments=()
    for environment in "${ALL_ENVIRONMENTS[@]}"
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

_build_completions() {
    load_containers ${COMP_WORDS[1]}
    COMPREPLY=($(compgen -W "${CONTAINERS[*]}" "${COMP_WORDS[3]}"))
}

_log_completions() {
    env_file=$(get_config ${COMP_WORDS[1]} "_ENV" ${ALL_ENVIRONMENTS[@]})
    if [ -f $env_file ]; then
        source $env_file

        local pod_array=($(kubectl get pods -o json | jq '.items[].metadata.name' | grep $APP))

        local i
        local args=()
        for i in "${pod_array[@]}"
        do
            i="${i%\"}"
            i="${i#\"}"
            args+=( $i )
        done

        COMPREPLY=($(compgen -W "${args[*]}" "${COMP_WORDS[3]}"))
    fi
}