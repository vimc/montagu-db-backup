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

if $GIT_BRANCH -eq "i1771"; then
    docker push $PUBLIC_REGISTRY/$NAME:$GIT_BRANCH
fi
