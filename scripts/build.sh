#!/usr/bin/env bash
#
# Build the RPMs in this repository, in dependency order.
#
# Usage:
#   scripts/build.sh              # build everything listed in packages.order
#   scripts/build.sh mango        # build only the named package(s)
#
# This installs build dependencies and writes to /etc/yum.repos.d, so it is
# meant to run as root inside a disposable Fedora container. See README.md for
# the podman one-liner and .woodpecker/build.yaml for the CI invocation.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOPDIR="${REPO_ROOT}/_build"
OUTPUT="${REPO_ROOT}/output"
LOCAL_REPO="rpm-builds-local"

if [ "$(id -u)" -ne 0 ]; then
    cat >&2 <<'EOF'
error: this script must run as root in a throwaway container.

It installs build dependencies with dnf and drops a repo file into
/etc/yum.repos.d, neither of which should happen on your daily-driver system.
Run it like this instead:

  podman run --rm -v "$PWD:/w:Z" -w /w registry.fedoraproject.org/fedora:44 \
    sh -c 'dnf -y install rpm-build rpmdevtools dnf5-plugins createrepo_c && ./scripts/build.sh'
EOF
    exit 1
fi

cd "${REPO_ROOT}"

if [ "$#" -gt 0 ]; then
    packages=("$@")
else
    mapfile -t packages < <(grep -vE '^[[:space:]]*(#|$)' packages.order)
fi

if [ "${#packages[@]}" -eq 0 ]; then
    echo "error: nothing to build" >&2
    exit 1
fi

mkdir -p "${TOPDIR}"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS} "${OUTPUT}"

# Expose output/ as a dnf repo so a package built earlier in this run can
# satisfy the BuildRequires of one built later -- that is how mango finds the
# scenefx-devel we just produced. Keeping this generic means adding a future
# package with an intra-repo dependency needs no change to this script, only a
# new line in packages.order.
createrepo_c --quiet --update "${OUTPUT}"
cat > "/etc/yum.repos.d/${LOCAL_REPO}.repo" <<EOF
[${LOCAL_REPO}]
name=RPMs built locally by this repository
baseurl=file://${OUTPUT}
enabled=1
gpgcheck=0
metadata_expire=0
EOF

for pkg in "${packages[@]}"; do
    spec="packages/${pkg}/${pkg}.spec"
    if [ ! -f "${spec}" ]; then
        echo "error: no such spec: ${spec}" >&2
        exit 1
    fi

    echo "==> ${pkg}: fetching sources"
    spectool --define "_topdir ${TOPDIR}" --get-files --sourcedir "${spec}"

    echo "==> ${pkg}: installing build dependencies"
    # --refresh so the local repo metadata regenerated below is picked up
    # rather than a stale cache from an earlier package in this same loop.
    dnf -y --refresh builddep "${spec}"

    echo "==> ${pkg}: rpmbuild"
    rpmbuild --define "_topdir ${TOPDIR}" -ba "${spec}"

    find "${TOPDIR}/RPMS" "${TOPDIR}/SRPMS" -name '*.rpm' -exec cp -f -t "${OUTPUT}" {} +
    createrepo_c --quiet --update "${OUTPUT}"
done

echo
echo "==> artifacts in ${OUTPUT}"
(cd "${OUTPUT}" && sha256sum ./*.rpm)
