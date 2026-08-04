# rpm-builds

RPM spec files for tools that are not in the Fedora repositories, or that Fedora
ships too old, built by Woodpecker CI. Targets **Fedora 44, x86_64**.

## Packages

| Package | Version | Workflow | Upstream |
| --- | --- | --- | --- |
| `scenefx`, `scenefx-devel` | 0.5.0 (tag `0.5`) | `mangowm` | <https://github.com/wlrfx/scenefx> |
| `mangowm` | 0.15.6 | `mangowm` | <https://github.com/mangowm/mango> |
| `fish` | 4.8.1 | `fish` | <https://github.com/fish-shell/fish-shell> |
| `noctalia` | 5.0.0~beta.7 | `noctalia` | <https://github.com/noctalia-dev/noctalia> |

`mangowm` is the MangoWM Wayland compositor. The package is named `mangowm` to
match what other repositories (Terra among them) call it, while upstream's GitHub
repo is `mangowm/mango` — `mangowm` is the org, `mango` the repo. That split runs
through the whole package: the tarball unpacks into `mango-<version>/`, so the
spec needs `%autosetup -n mango-%{version}`, and the installed binary and config
paths are all `mango`. Do not "harmonise" those to `mangowm`.

Its upstream build instructions tell you to build wlroots by hand, but that is not
needed on Fedora 44 — the distro already ships `wlroots-0.20.2` and a
`wlroots-devel` providing `wlroots-0.20.pc`, which is exactly what both `scenefx`
and `mangowm` ask for. Building a second copy into `/usr` would collide with the
distro package.

`scenefx` exists here only because `mangowm` links against it, so the two share
one workflow.

`fish` is here because Fedora 44 ships 4.6.0. It is a Rust build, and its release
tarball contains no vendored crates, so the workflow runs `cargo vendor` and
hands the result to the spec as `Source3`; `%build` then runs with
`CARGO_NET_OFFLINE=true`. That keeps the SRPM self-contained — it can be rebuilt
with no network at all — and sidesteps the five-patch stack Fedora needs to strip
fish's four git dependencies. The release signature is verified against the
upstream maintainer's key during `%prep`.

`noctalia` is a Wayland desktop shell — bars, dock, launcher, notifications, lock
screen, wallpaper and settings in one binary — and Fedora does not ship it. Note
that v5 is a C++23/Meson rewrite with **no Qt and no GTK**, drawing on Wayland and
OpenGL ES directly. v4 was the Quickshell/QML configuration packaged elsewhere as
`noctalia-shell`, which is what Repology may still show; none of that applies here,
and nothing needs a `quickshell` package.

Upstream is still in beta and tags releases `v5.0.0-beta.N`, which RPM cannot use
verbatim because a hyphen separates Version from Release. The spec uses
`5.0.0~beta.7` instead: a tilde sorts below everything, so the 5.0.0 final will
upgrade cleanly with no epoch. The hyphenated form stays in `%global
upstream_version` for the tag URL and the unpack directory, so a beta bump edits
two lines rather than one.

Upstream's README has a copy-paste `dnf install` line for Fedora that does not
work on Fedora 44: it names `libEGL-devel` and `mesa-libGLES-devel`, neither of
which is a Fedora 44 package. Asking for `pkgconfig(egl)` and `pkgconfig(glesv2)`
resolves to `libglvnd-devel`, which is why the spec uses the pkg-config names.

noctalia's workflow is also the one place where `git` has to be installed *and*
fenced off at the same time. Its test suite drives real repositories, so git must
be on `PATH`, but that makes meson's `vcs_tag()` run `git describe` — which walks
up out of the build tree, finds *this* repository, and reports its tag
(`fish-4.8.1-1-dirty`) as noctalia's revision. The spec sets
`GIT_CEILING_DIRECTORIES=%{_builddir}` in `%build` and `%check` to stop that walk,
after which `describe` fails and `vcs_tag` uses its own `unknown` fallback. This is
the same hazard mangowm dodges by leaving git out entirely; noctalia cannot, so it
fences instead. `GIT_DIR` is not a substitute — it suppresses discovery everywhere
and breaks the tests' own repositories.

fish's and noctalia's workflows drop privileges before `rpmbuild`, because their
test suites assert on file permissions and root bypasses those. For fish it is
tests over unreadable files; for noctalia it is
`calendar_cache_permissions`, `clipboard_storage_permissions`,
`plugin_source_locks` and `secret_store`. Fedora avoids this for free because mock
builds as a non-root user.

## Layout

```
.woodpecker/<workflow>.yaml    one workflow per thing you want to build
packages/<name>/<name>.spec    one directory per source package
```

Each file in `.woodpecker/` is an independent workflow. Woodpecker runs them in
parallel on separate agents, and each one matches only its own tag prefix, so
tagging one package does not rebuild the others. A package with a build
dependency on another (mangowm on scenefx) just builds both in one workflow and
`dnf install`s the intermediate result.

There is no build script and no ordering file — ordering is the order of the
commands in a workflow, and dependencies are whatever that workflow installs.

## Adding a package

1. `packages/<name>/<name>.spec`
2. `.woodpecker/<name>.yaml` — copy an existing one and change the spec paths and
   the `ref:` tag prefix.

## Building locally

CI only runs on tags, so this is where a spec gets verified before it is tagged —
a build error found here costs nothing, whereas one found in CI costs a `Release`
bump and a second tag.

The CI definition is the build definition, so run it with the Woodpecker CLI
rather than reimplementing it:

```sh
woodpecker-cli exec .woodpecker/mangowm.yaml
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

**Do not start a second `:Z` container against this directory while a build is
running.** `:Z` relabels the bind mount with the *calling* container's SELinux MCS
category, so a second container silently steals the label out from under the first
one and every file the running build touches from then on fails. It does not look
like a permission problem either: the symptoms are hundreds of
`as: BFD ... assertion fail`, a bogus `No space left on device` on a disk with
600 GB free, and `Permission denied` in a directory that has already accepted
hundreds of object files. If you want to inspect or validate something mid-build,
either wait, or mount read-only (`:z,ro`) — a shared label does not get stolen.

Cleaning up afterwards: fish's and noctalia's workflows build as an unprivileged
user, and under rootless podman that leaves `_build` owned by a subuid your
account cannot delete. `rm -rf _build` fails with "Permission denied"; use this
instead:

```sh
podman unshare rm -rf _build
```

## Publishing

**A tag is the only thing that runs CI at all.** Pushing a commit builds nothing,
and there is no manual trigger — so a tag always ends in a publish, and the spec
has to be checked locally before it is tagged (see [Building
locally](#building-locally)). RPMs would not survive a non-publishing run anyway,
because Woodpecker has no artifact store
([#1014](https://github.com/woodpecker-ci/woodpecker/issues/1014), closed as
by-design).

Tag names decide what publishes, and the prefix must match the workflow:

| Tag | Publishes |
| --- | --- |
| `fish-4.8.1-1` | `fish` |
| `mangowm-0.15.6-1` | `mangowm` and `scenefx` |
| `scenefx-0.5.0-1` | `mangowm` and `scenefx` |
| `noctalia-5.0.0~beta.7-1` | `noctalia` |

```sh
git tag fish-4.8.1-1 && git push --tags
```

Tags are matched on `ref` rather than on changed paths, because a path filter is
evaluated against a diff and what a tag diffs against is not worth relying on.

If a tagged build fails, fix the spec and tag again with `Release` bumped — e.g.
`mangowm-0.15.6-2`. Do not force-push the existing tag: whether Woodpecker treats
a moved tag as a fresh `tag` event is unconfirmed, and a tag that moves no longer
identifies what is in the repo. This also means the Woodpecker repo settings must
keep **Tag** in *Allowed events*; that setting is not in version control.

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
sudo dnf install mangowm fish
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
