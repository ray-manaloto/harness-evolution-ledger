#!/usr/bin/env bash
set -euo pipefail

readonly mise_version="2026.8.14"
readonly user_mise_dir="${HOME}/.local/bin"

mkdir -p "${user_mise_dir}"
cp /usr/local/bin/mise "${user_mise_dir}/mise"
"${user_mise_dir}/mise" self-update "${mise_version}" --yes --no-plugins
export PATH="${user_mise_dir}:${PATH}"

actual_version="$(mise --version)"
case "${actual_version}" in
"${mise_version} "*) ;;
*)
	printf 'unexpected mise version after update: %s\n' "${actual_version}" >&2
	exit 2
	;;
esac

mise trust ./mise.toml
mise install --locked
mise run doctor
mise run check
