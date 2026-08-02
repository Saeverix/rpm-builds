# rpm-builds

RPM spec files for tools that are not in the Fedora repositories, built by
Woodpecker CI. Currently targets **Fedora 44, x86_64**.

## Packages

| Package | Version | Upstream |
| --- | --- | --- |
| `scenefx`, `scenefx-devel` | 0.5.0 (tag `0.5`) | <https://github.com/wlrfx/scenefx> |
| `mango` | 0.15.5 | <https://github.com/mangowm/mango> |

`mango` is the MangoWM Wayland compositor. Its upstream build instructions tell
you to build wlroots by hand, but that is not needed on Fedora 44 — the distro
already ships `wlroots-0.20.2` and a `wlroots-devel` providing
`wlroots-0.20.pc`, which is exactly what both `scenefx` and `mango` ask for.
Building a second copy into `/usr` would collide with the distro package. Only
`scenefx` and `mango` are built here.

`mango` links against `scenefx`, so `scenefx` is built first and published into
a throwaway local dnf repo that `mango`'s `dnf builddep` then resolves against.

## Building locally

`scripts/build.sh` installs build dependencies and writes to
`/etc/yum.repos.d`, so run it as root in a disposable container, never on your
own system:

```sh
podman run --rm -v "$PWD:/w:Z" -w /w registry.fedoraproject.org/fedora:44 \
  sh -c 'dnf -y install rpm-build rpmdevtools dnf5-plugins createrepo_c && ./scripts/build.sh'
```

The finished RPMs and SRPMs end up in `output/`. To rebuild a single package:

```sh
./scripts/build.sh mango
```

## CI

`.woodpecker/build.yaml` runs the same script in a `fedora:44` container on
push, pull request and manual trigger.

Woodpecker has no built-in artifact store, so today the pipeline verifies that
everything builds and prints sha256sums, but the RPMs themselves are discarded
when the pipeline ends. Use the local podman command above when you actually
want an installable RPM. `build.yaml` has commented-out publish steps for a
Gitea release or an rsync-to-webserver dnf repo when you want to change that.

## Adding a package

1. `packages/<name>/<name>.spec`
2. Add `<name>` to `packages.order`, after anything it BuildRequires.

Nothing else needs changing — `scripts/build.sh` is generic.

## Conventions

- Versions are pinned to upstream release tags. To update a package, bump
  `Version` (and `%global tag` where upstream's tag differs from its version,
  as with scenefx) and reset `Release` to `1%{?dist}`.
- Non-obvious packaging decisions are commented in the spec files themselves,
  next to the line they apply to. There are a few that look like mistakes and
  are not — read the comment before "fixing" one.
