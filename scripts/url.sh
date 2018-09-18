#!/bin/bash

url_kube() {
	contains $environment ${MINIKUBE_ENVIRONMENTS[@]}
	if [ $? -eq 1 ]; then
		minikube service $APP --url
		exit
	fi

	contains $environment ${KUBE_ENVIRONMENTS[@]}
	if [ $? -eq 1 ]; then
		local array=($(kubectl get services --field-selector=metadata.name=$APP -o json | jq '.items[0].status.loadBalancer.ingress[0].ip , .items[0].spec.ports[0].targetPort'))
		local ip=${array[0]}
		local port=${array[1]}
		ip="${ip%\"}"
		ip="${ip#\"}"
		echo "http://$ip:$port/"
		exit
	fi
}