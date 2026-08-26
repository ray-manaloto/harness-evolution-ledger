# Immutable devcontainer input

The container consumes the dotfiles-owned image without depending on a sibling
checkout or copying its hooks and Python modules.

- Producer repository: `ray-manaloto/dotfiles`
- Producer commit inspected: `362f3ed8dbff92c75428c532d7ddf8c2bb48ca63`
- Selected arm64 OCI revision label:
  `2108ebf345acd2c3275da46a1adc048b9b39cecc` (recorded drift from the
  separately inspected producer commit)
- OCI index digest:
  `sha256:d57c2b5dbddb8e08571dee86bbb9f239957691454de85a1401239da9396d0012`
- amd64 manifest:
  `sha256:f74cee44f80fd795f5cb8ad85238048d75653eaa2b2da43957dd168a405cab37`
- arm64 manifest:
  `sha256:61b447716be70105cce0884258ee882e266e8974f227892b529e54a1061fce1e`

The checked-in configuration selects the immutable multi-architecture index.
Docker resolves that index to the recorded amd64 or arm64 manifest for the host;
clean clones therefore use one reviewed identity without a mutable tag or a
platform-specific source edit.

The image supplies Linux/compiler capabilities. This repository's `mise.toml`,
`mise.lock`, hooks, rules, and public tasks remain the project contract. No host
secret file or broad environment is mounted into the container.

The image contains mise 2026.8.5 and disables GitHub-attestation and SLSA
verification in its system config. The project post-create handler installs a
user-local mise 2026.8.13, while `mise.toml` explicitly re-enables both provenance
controls before the locked install. The image's non-root user is `ubuntu`; it has no
`devcontainer` account.

The `container-debug` preset uses
`/opt/clang-p2996/bin/clang++` and a container-only build directory. The current
image's `/opt/gcc-latest/bin/g++` reports 15.2.0, so GCC 16.2 release-authority
validation remains unavailable rather than being inferred from the directory name.
