#!/bin/bash

url_minikube() {
	minikube service $APP --url
}

url_kube() {
	local array=($(kubectl get services --field-selector=metadata.name=$APP -o json | jq '.items[0].status.loadBalancer.ingress[0].ip , .items[0].spec.ports[0].targetPort'))
	local ip=${array[0]}
	local port=${array[1]}
	ip="${ip%\"}"
	ip="${ip#\"}"
    echo "http://$ip:$port/"
}