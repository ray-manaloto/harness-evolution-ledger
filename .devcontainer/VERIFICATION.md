# Devcontainer verification

Verified on 2026-08-25 (America/Chicago) from clean branch
`codex/devcontainer-setup`, based on `origin/main` at
`e97e00a5916235389685b5b3baab26b409b01dd7`.

## Immutable inputs

- Remote dotfiles source inspected at
  `ray-manaloto/dotfiles@362f3ed8dbff92c75428c532d7ddf8c2bb48ca63`.
- Published OCI index:
  `ghcr.io/ray-manaloto/dotfiles-devcontainer@sha256:d57c2b5dbddb8e08571dee86bbb9f239957691454de85a1401239da9396d0012`.
- Dev Container CLI: `0.88.0` (Node.js `v26.7.0`, darwin arm64).
- Docker: `29.7.2`, OrbStack engine.

No Python library code was downloaded. The immutable image already contains the
runtime; this repository needs only a user, workspace mount, and marker variable.

## Positive controls

All commands ran from the clean replacement worktree. The worktree basename is
`harness-evolution-ledger-devcontainer`, so the parameterized workspace path
expanded to `/workspaces/harness-evolution-ledger-devcontainer` for these runs.

### Configuration

```console
$ devcontainer read-configuration --workspace-folder .
... "image":"ghcr.io/ray-manaloto/dotfiles-devcontainer@sha256:d57c2b5dbddb8e08571dee86bbb9f239957691454de85a1401239da9396d0012" ...
... "workspaceFolder":"/workspaces/harness-evolution-ledger-devcontainer" ...
... "workspaceMount":"source=/Users/rmanaloto/dev/github/ray-manaloto/harness-evolution-ledger-devcontainer,target=/workspaces/harness-evolution-ledger-devcontainer,type=bind,consistency=cached" ...
exit 0
```

### Image pull and container startup

```console
$ docker pull ghcr.io/ray-manaloto/dotfiles-devcontainer@sha256:d57c2b5dbddb8e08571dee86bbb9f239957691454de85a1401239da9396d0012
Digest: sha256:d57c2b5dbddb8e08571dee86bbb9f239957691454de85a1401239da9396d0012
Status: Image is up to date for ghcr.io/ray-manaloto/dotfiles-devcontainer@sha256:d57c2b5dbddb8e08571dee86bbb9f239957691454de85a1401239da9396d0012
exit 0

$ devcontainer up --workspace-folder .
Container started
{"outcome":"success","containerId":"0f2552ed3a8c8ff7f216271e6ab99c4ff0de1fad504919f4f575d10de3b31fa9","remoteUser":"ubuntu","remoteWorkspaceFolder":"/workspaces/harness-evolution-ledger-devcontainer"}
exit 0
```

### In-container and Docker controls

```console
$ devcontainer exec --workspace-folder . /usr/bin/id -un
ubuntu
exit 0

$ devcontainer exec --workspace-folder . /bin/pwd
/workspaces/harness-evolution-ledger-devcontainer
exit 0

$ devcontainer exec --workspace-folder . /usr/bin/test -f .devcontainer/devcontainer.json
exit 0

$ docker inspect 0f2552ed3a8c8ff7f216271e6ab99c4ff0de1fad504919f4f575d10de3b31fa9 --format '{{json .Mounts}}'
[{"Type":"bind","Source":"/Users/rmanaloto/dev/github/ray-manaloto/harness-evolution-ledger-devcontainer","Destination":"/workspaces/harness-evolution-ledger-devcontainer","Mode":"","RW":true,"Propagation":"rprivate"}]
exit 0

$ docker inspect 0f2552ed3a8c8ff7f216271e6ab99c4ff0de1fad504919f4f575d10de3b31fa9 --format 'image_id={{.Image}} configured_user={{json .Config.User}} devcontainer={{range .Config.Env}}{{if eq . "DEVCONTAINER=true"}}{{.}}{{end}}{{end}}'
image_id=sha256:d57c2b5dbddb8e08571dee86bbb9f239957691454de85a1401239da9396d0012 configured_user="" devcontainer=DEVCONTAINER=true
exit 0
```

An empty Docker `Config.User` is expected because `remoteUser` controls editor
and `devcontainer exec` sessions rather than changing the image's default user.
The positive `id -un` control above proves those sessions run as `ubuntu`.

## Warning retained

The first composite probe used nested shell evaluation:

```console
$ devcontainer exec --workspace-folder . /bin/sh -lc '<combined assertions>'
/bin/sh: 18: eval: Syntax error: "(" unexpected (expecting "fi")
exit 2
```

This is an image shell-initialization/quoting interaction. Direct argument-safe
commands then proved the required user, workspace, environment marker, and mount
without suppressing or changing image behavior.

## Boundaries

- No secrets, credential files, host home, SSH agent, Docker socket, or broad
  host environment are mounted or persisted by this configuration.
- This task is attached to the `local-model-eval` saved project. It therefore
  does not prove Harness Evolution Ledger project instruction or hook loading.
