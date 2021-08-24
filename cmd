#!/bin/bash

## Available commands
#
#  *** to build image(s) ***
#  ./cmd build
#  ./cmd build image1
#  ./cmd build image1 image2
#
# *** to run containers in development mode ***
# ./cmd dev
#
# *** to run containers in production mode ***
# ./cmd prod
#
# *** to stop containers ***
# ./cmd stop

command=$1
arr=("$@")

run_in_development() {
    sudo docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
    echo "========== finished running with docker-compose in development mode =========="
}

run_in_production() {
    sudo docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    echo "========== finished running with docker-compose in production mode =========="
}

stop_containers() {
    sudo docker-compose down
    echo "========== stopped containers =========="
}

build_images() {
    echo "========== start building images for [${arr[@]}] =========="
    sudo docker-compose build ${arr[@]}
    echo "========== finished building images for [${arr[@]}] =========="
}

if [[ $command = "build" ]] || [[ $command == "rebuild" ]] 
then
    unset arr[0]
    build_images ${arr[@]}
elif [[ $command = "dev" ]]
then
    run_in_development
elif [[ $command = "prod" ]]
then
    run_in_production
elif [[ $command = "stop" ]]
then
    stop_containers
else
    echo "entered a wrong command, available commands are: [build, dev, prod]"
fi