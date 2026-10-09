#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

API_IMAGE="distributed-systems-lab/api:latest"
DEPENDENCY_IMAGE="distributed-systems-lab/dependency:latest"
NETWORK="lab-network"
CLUSTER="distributed-systems-lab"

echo "==> Building application images"

docker build --provenance=false -t "$API_IMAGE" applications/api
docker build --provenance=false -t "$DEPENDENCY_IMAGE" applications/dependency

echo "==> Preparing Docker environment"

if ! docker network inspect "$NETWORK" >/dev/null 2>&1; then
    docker network create "$NETWORK"
fi

ensure_container() {
    local name="$1"
    local image="$2"
    local port_mapping="${3:-}"
    local desired_image_id

    desired_image_id="$(docker image inspect "$image" --format '{{.Id}}')"

    if docker container inspect "$name" >/dev/null 2>&1; then
        local current_image_id
        current_image_id="$(docker container inspect "$name" --format '{{.Image}}')"

        if [[ "$current_image_id" != "$desired_image_id" ]]; then
            echo "Container '$name' uses an outdated image; recreating it."
            docker rm -f "$name" >/dev/null
        else
            if [[ "$(docker container inspect "$name" --format '{{.State.Running}}')" != "true" ]]; then
                echo "Starting stopped container '$name'."
                docker start "$name" >/dev/null
            else
                echo "Container '$name' is already up to date."
            fi
            return
        fi
    fi

    local args=(docker run -d --name "$name" --network "$NETWORK")

    if [[ -n "$port_mapping" ]]; then
        args+=(-p "$port_mapping")
    fi

    args+=("$image")
    "${args[@]}" >/dev/null
    echo "Created container '$name'."
}

ensure_container api "$API_IMAGE" "8080:8080"
ensure_container dependency "$DEPENDENCY_IMAGE"

echo "==> Preparing Kubernetes cluster"

if ! kind get clusters | grep -Fxq "$CLUSTER"; then
    kind create cluster \
        --name "$CLUSTER" \
        --config k8s/kind-config.yaml
else
    echo "Kind cluster '$CLUSTER' already exists."
fi

echo "==> Loading images into Kind"

kind load docker-image "$API_IMAGE" "$DEPENDENCY_IMAGE" \
    --name "$CLUSTER"

echo "==> Applying Kubernetes manifests"

kubectl --context "kind-$CLUSTER" apply \
    -f k8s/dependency.yaml \
    -f k8s/dependency-service.yaml \
    -f k8s/api.yaml \
    -f k8s/api-service.yaml

echo "==> Updating Kubernetes deployments when build inputs change"

API_BUILD_HASH="$(find applications/api -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -d ' ' -f 1)"
DEPENDENCY_BUILD_HASH="$(find applications/dependency -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -d ' ' -f 1)"

kubectl --context "kind-$CLUSTER" patch deployment api --type merge \
    -p "{\"spec\":{\"template\":{\"metadata\":{\"annotations\":{\"lab.distributed-systems/build-hash\":\"$API_BUILD_HASH\"}}}}}"

kubectl --context "kind-$CLUSTER" patch deployment dependency --type merge \
    -p "{\"spec\":{\"template\":{\"metadata\":{\"annotations\":{\"lab.distributed-systems/build-hash\":\"$DEPENDENCY_BUILD_HASH\"}}}}}"

echo "==> Waiting for Kubernetes deployments"

kubectl --context "kind-$CLUSTER" rollout status deployment/dependency
kubectl --context "kind-$CLUSTER" rollout status deployment/api

echo "==> Setup complete"
