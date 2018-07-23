#!/usr/bin/env bash
set -e

GIT_ID=$(git rev-parse --short=7 HEAD)
GIT_BRANCH=$(git symbolic-ref --short HEAD)
REGISTRY=docker.montagu.dide.ic.ac.uk:5000
PUBLIC_REGISTRY=vimc
NAME=montagu-barman

APP_DOCKER_TAG=$REGISTRY/$NAME
APP_DOCKER_COMMIT_TAG=$REGISTRY/$NAME:$GIT_ID
APP_DOCKER_BRANCH_TAG=$REGISTRY/$NAME:$GIT_BRANCH

docker build --pull \
       --tag $APP_DOCKER_COMMIT_TAG \
       --tag $APP_DOCKER_BRANCH_TAG \
       .

docker push $APP_DOCKER_BRANCH_TAG
docker push $APP_DOCKER_COMMIT_TAG

if [[ $GIT_BRANCH -eq "master" ]]; then  # TODO: return to master
    PUBLIC_TAG=$PUBLIC_REGISTRY/$NAME:master
    docker tag $APP_DOCKER_BRANCH_TAG $PUBLIC_TAG
    docker push $PUBLIC_TAG
fi
