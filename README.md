# rpm-builds

RPM spec files for tools that are not in the Fedora repositories, or that Fedora
ships too old, built by Woodpecker CI. Targets **Fedora 44, x86_64**.

## Packages

| Package | Version | Workflow | Upstream |
| --- | --- | --- | --- |
| `scenefx`, `scenefx-devel` | 0.5.0 (tag `0.5`) | `mango` | <https://github.com/wlrfx/scenefx> |
| `mango` | 0.15.5 | `mango` | <https://github.com/mangowm/mango> |
| `fish` | 4.8.1 | `fish` | <https://github.com/fish-shell/fish-shell> |

`mango` is the MangoWM Wayland compositor. Its upstream build instructions tell
you to build wlroots by hand, but that is not needed on Fedora 44 — the distro
already ships `wlroots-0.20.2` and a `wlroots-devel` providing `wlroots-0.20.pc`,
which is exactly what both `scenefx` and `mango` ask for. Building a second copy
into `/usr` would collide with the distro package.

`scenefx` exists here only because `mango` links against it, so the two share one
workflow.

`fish` is here because Fedora 44 ships 4.6.0. It is a Rust build, and its release
tarball contains no vendored crates, so the workflow runs `cargo vendor` and
hands the result to the spec as `Source3`; `%build` then runs with
`CARGO_NET_OFFLINE=true`. That keeps the SRPM self-contained — it can be rebuilt
with no network at all — and sidesteps the five-patch stack Fedora needs to strip
fish's four git dependencies. The release signature is verified against the
upstream maintainer's key during `%prep`.

fish's workflow also drops privileges before `rpmbuild`, because its test suite
asserts on unreadable files and root bypasses those permissions: as root 197/203
tests pass, as an unprivileged user 201/201. Fedora avoids this for free because
mock builds as a non-root user.

## Layout

```
.woodpecker/<workflow>.yaml    one workflow per thing you want to build
packages/<name>/<name>.spec    one directory per source package
```

Each file in `.woodpecker/` is an independent workflow. Woodpecker runs them in
parallel on separate agents, and each one carries a `when: path:` filter so
touching one package's spec does not rebuild the others. A package with a build
dependency on another (mango on scenefx) just builds both in one workflow and
`dnf install`s the intermediate result.

There is no build script and no ordering file — ordering is the order of the
commands in a workflow, and dependencies are whatever that workflow installs.

## Adding a package

1. `packages/<name>/<name>.spec`
2. `.woodpecker/<name>.yaml` — copy an existing one and change the spec paths and
   the `path:` filter.

## Building locally

The CI definition is the build definition, so run it with the Woodpecker CLI
rather than reimplementing it:

```sh
woodpecker-cli exec .woodpecker/mango.yaml
```

> Not yet verified whether `woodpecker-cli exec` leaves `output/` in your working
> directory or in a throwaway volume. If it is the latter, use the fallback
> below when you actually want an installable RPM.

Fallback without the CLI — extract the workflow's own commands and run them in a
container, with the workspace bind-mounted so the RPMs survive. Change the
filename to pick a different package:

```sh
podman run --rm -v "$PWD:/w:Z" -w /w registry.fedoraproject.org/fedora:44 sh -c '
  dnf -y install python3-pyyaml >/dev/null 2>&1
  python3 - <<PY > /tmp/step.sh
import yaml
print("set -ex")
print("\n".join(yaml.safe_load(open(".woodpecker/fish.yaml"))["steps"][0]["commands"]))
PY
  sh /tmp/step.sh'
```

**Do not hand-copy the commands into a script instead.** Woodpecker joins a
step's commands into one shell, so state leaks between them; a transcription that
drifted from the YAML by a single `cd` is exactly how a working-directory bug
once reached CI while passing locally. Running the YAML is the only faithful test.

Cleaning up afterwards: fish's workflow builds as an unprivileged user, and under
rootless podman that leaves `_build` owned by a subuid your account cannot delete.
`rm -rf _build` fails with "Permission denied"; use this instead:

```sh
podman unshare rm -rf _build
```

## Publishing

Each workflow ends with a `publish` step that ships its RPMs to a dnf repo hosted
on the K3s cluster. It runs **on tags only** — a plain push still builds and
verifies, then throws the RPMs away, because Woodpecker has no artifact store
([#1014](https://github.com/woodpecker-ci/woodpecker/issues/1014), closed as
by-design).

Tag names decide what publishes, and the prefix must match the workflow:

| Tag | Publishes |
| --- | --- |
| `fish-4.8.1-1` | `fish` |
| `mango-0.15.5-1` | `mango` and `scenefx` |
| `scenefx-0.5.0-1` | `mango` and `scenefx` |

```sh
git tag fish-4.8.1-1 && git push --tags
```

Tags are matched on `ref` rather than on changed paths, because a path filter is
evaluated against a diff and what a tag diffs against is not worth relying on.

### Triggering by hand

The Woodpecker server is only reachable on the LAN, so GitHub cannot deliver the
webhook a tag push needs — until that changes, tags build nothing on their own.
Trigger a manual pipeline instead and set a `PACKAGE` variable to pick the
workflow:

| `PACKAGE` | Runs |
| --- | --- |
| `mango` | `mango.yaml` — builds and publishes scenefx, scenefx-devel, mango |
| `fish` | `fish.yaml` — builds and publishes fish |

Omitting the variable matches neither workflow and the pipeline does nothing;
that is deliberate, so a stray manual run does not rebuild every package. Manual
runs publish, which tag-only runs would not — the `manual` entry in each publish
step's `when:` is there purely to cover the missing webhook, and should be
removed once tags work.

Only binary RPMs are published. `-debuginfo`, `-debugsource` and the SRPM are
filtered out — they are all rebuildable from the tagged spec. The repo keeps the
newest three builds of each package, so a bad bump can be downgraded away; older
ones are pruned by `dnf repomanage` before the metadata is regenerated.

Everything is GPG-signed, and the private key never leaves the publish step.
Because the metadata is generated in the cluster, `repomd.xml` cannot be signed
at the moment it is written; instead `createrepo_c` runs over ssh, the finished
`repomd.xml` comes back here, gets signed where the key already is, and only the
detached signature goes up. Clients therefore get both `gpgcheck=1` and
`repo_gpgcheck=1`.

Do not verify the signing with a `%{SIGPGP}` tag check. That is the legacy
signature tag and reads `(none)` on rpm 4.20 even for a correctly signed package,
so it rejects every build; the step imports the public key and lets `rpm -Kv`
verify instead.

The cluster manifests are **not** in this repo — they live in the `homelab` repo
under `apps/rpm-repo/`, which also serves the client `.repo` file and the public
key. Installing on a Fedora box:

```sh
sudo curl -o /etc/yum.repos.d/saeverix.repo https://rpm.<dev-domain>/saeverix.repo
sudo rpm --import https://rpm.<dev-domain>/RPM-GPG-KEY-saeverix
sudo dnf install mango fish
```

Woodpecker secrets the publish step needs: `rpm_repo_host`, `rpm_ssh_key`,
`rpm_ssh_known_hosts`, `rpm_gpg_key`.

## Conventions

- `%changelog` entries are attributed to `Saeverix`, with no email address. RPM
  treats everything after the date as free text, so the address Fedora's
  guidelines use is optional. If you add entries with `rpmdev-bumpspec`, pass
  `-u Saeverix` or it will reintroduce one.
- Versions are pinned to upstream release tags. To update a package, bump
  `Version` (and `%global tag` where upstream's tag differs from its version, as
  with scenefx) and reset `Release` to `1%{?dist}`.
- Non-obvious packaging decisions are commented in the spec files themselves,
  next to the line they apply to. A few look like mistakes and are not — read the
  comment before "fixing" one.
