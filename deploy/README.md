# Nomad Deployment

This directory contains a minimal HashiCorp Nomad deployment targeting the `catalog` and `datasets`
services. It provides build scripts for container images and a single job specification that can be
parameterised for development or production environments.

## Prerequisites

- Docker (or another container runtime compatible with the Nomad Docker driver)
- HashiCorp Nomad CLI configured to talk to your cluster
- HashiCorp Consul agent (run `consul agent -dev` locally to mirror production service discovery)
- Optional: A container registry to publish the built images

## Layout

- `scripts/build-images.sh` – convenience script that builds the service images from the repository root.
- `nomad/agentic-rag.nomad.hcl` – Nomad job specification for both services. Supply variables at submit
  time to pick the environment, datacenters, and image tags.

## Building Images

```bash
./deploy/scripts/build-images.sh
```

The script builds `agentic-rag/catalog:<tag>` and `agentic-rag/datasets:<tag>` images (defaults to
`dev`). Override the tag by exporting `IMAGE_TAG` before running the script. The build script
passes `--network host` to `docker build` by default to ensure the build container has outbound
network access. Adjust via `DOCKER_BUILD_NETWORK` if your environment requires a different setting.

Push the images to your registry of choice once built:

```bash
docker push agentic-rag/catalog:<tag>
docker push agentic-rag/datasets:<tag>
```

## Running the Job

For local development, launch the dependency agents first:

```bash
consul agent -dev -ui &
sudo nomad agent -dev -config=deploy/nomad/dev.hcl -consul-address=127.0.0.1:8500
```

In a separate terminal, submit the job, overriding variables as needed:

```bash
tag=dev
nomad job run \
  -var environment=dev \
  -var catalog_image=agentic-rag/catalog:${tag} \
  -var datasets_image=agentic-rag/datasets:${tag} \
  deploy/nomad/agentic-rag.nomad.hcl
```

### Useful Variables

- `environment` – stored in Nomad job metadata and propagated to service registrations.
- `datacenters` – list of datacenters to target (`["dc1"]` by default).
- `catalog_image` / `datasets_image` – Docker images that Nomad should run.
- `catalog_count` / `datasets_count` – optional scaling knobs for each task group.
- `catalog_config_path` / `datasets_config_path` – configuration file paths inside the container,
  defaulting to the Nomad-specific YAML files committed in each service.

The Nomad job name is fixed to `agentic-rag`; stop the job with `nomad job stop agentic-rag`.
With Consul running (for example `consul agent -dev -ui`), the service registrations will appear in
the catalog and can be queried via `curl http://127.0.0.1:8500/v1/catalog/service/catalog-dev`.
Adjust checks, resources, and network definitions as your infrastructure matures.

The datasets task uses a Nomad template stanza to resolve the catalog service address from Consul
and exports it as `CATALOG_BASE_URL`, keeping inter-service calls aligned with dynamic allocations.

## install tools
See https://developer.hashicorp.com/nomad/docs/deploy
### install nomad
```shell
# prereqs
sudo apt-get update && sudo apt-get install -y wget gpg coreutils

# add official HashiCorp key (keyring, not apt-key)
wget -O- https://apt.releases.hashicorp.com/gpg \
| sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg

# add repo (auto-detects your Ubuntu codename)
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(grep -oP '(?<=UBUNTU_CODENAME=).*' /etc/os-release || lsb_release -cs) main" \
| sudo tee /etc/apt/sources.list.d/hashicorp.list

# install
sudo apt-get update && sudo apt-get install -y nomad
```

May need post installation steps for cni etc, please consult the hashicorp page.
