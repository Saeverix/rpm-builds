# rpm-builds

RPM spec files for tools that are not in the Fedora repositories, or that Fedora
ships too old, built by Woodpecker CI. Targets **Fedora 44** and **AlmaLinux 10**,
x86_64.

## Packages

| Package | Version | Workflow | Targets | Upstream |
| --- | --- | --- | --- | --- |
| `scenefx`, `scenefx-devel` | 0.5.0 (tag `0.5`) | `mangowm` | fc44 | <https://github.com/wlrfx/scenefx> |
| `mangowm` | 0.15.6 | `mangowm` | fc44 | <https://github.com/mangowm/mango> |
| `fish` | 4.8.1 | `fish` | fc44, el10 | <https://github.com/fish-shell/fish-shell> |
| `noctalia` | 5.0.0~beta.7 | `noctalia` | fc44 | <https://github.com/noctalia-dev/noctalia> |
| `hyprwayland-scanner-devel` | 0.4.6 | `hyprland` | fc44 | <https://github.com/hyprwm/hyprwayland-scanner> |
| `hyprland-protocols-devel` | 0.7.0 | `hyprland` | fc44 | <https://github.com/hyprwm/hyprland-protocols> |
| `glaze-devel` | 7.2.0 | `hyprland` | fc44 | <https://github.com/stephenberry/glaze> |
| `hyprutils`, `hyprutils-devel` | 0.14.0 | `hyprland` | fc44 | <https://github.com/hyprwm/hyprutils> |
| `hyprlang`, `hyprlang-devel` | 0.6.8 | `hyprland` | fc44 | <https://github.com/hyprwm/hyprlang> |
| `hyprwire`, `hyprwire-devel` | 0.3.1 | `hyprland` | fc44 | <https://github.com/hyprwm/hyprwire> |
| `hyprgraphics`, `hyprgraphics-devel` | 0.5.1 | `hyprland` | fc44 | <https://github.com/hyprwm/hyprgraphics> |
| `hyprcursor`, `hyprcursor-devel` | 0.1.13 | `hyprland` | fc44 | <https://github.com/hyprwm/hyprcursor> |
| `aquamarine`, `aquamarine-devel` | 0.13.0 | `hyprland` | fc44 | <https://github.com/hyprwm/aquamarine> |
| `hyprland`, `hyprland-devel` | 0.56.1 | `hyprland` | fc44 | <https://github.com/hyprwm/Hyprland> |

Only `fish` builds for AlmaLinux 10. For the rest the blockers are missing build
dependencies rather than anything in this repo:

- `noctalia` needs `pkgconfig(wireplumber-0.5)`. EL10 ships wireplumber 0.5.10 —
  the right version — but there is **no `wireplumber-devel` package at all**, and
  the runtime package carries no headers or `.pc` files. Everything else it wants
  is available, mostly through EPEL.
- `scenefx` and `mangowm` need wlroots 0.20; EPEL 10 has only 0.18.2. Note this
  inverts the reasoning below for not building wlroots by hand — on EL10 you would
  have to, turning the mangowm workflow into a three-package chain.
- The `hyprland` stack is Fedora 44 only because that is what it was asked for; EL10
  has not been attempted. Hyprland compiles as C++26, so EL10's compiler is the
  first thing that would need checking, before the ten-package chain is even worth
  starting.

An RPM is never shared between the two targets. EL10 is glibc 2.39 against Fedora
44's 2.43, sonames differ, and `%{?dist}` gives `.el10` rather than `.fc44`, so each
distro is a separate build producing its own NVR. One spec covers both, though —
`fish` needs no distro conditionals.

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

The tilde cannot appear in the **git tag**, though: `~` is revision syntax
(`HEAD~3`), so git rejects it in a ref name outright. Write it as a hyphen there —
`Version: 5.0.0~beta.7` is tagged `noctalia-5.0.0-beta.7-1`. That is the only
place the two forms differ, nothing parses the tag (the workflow just prefix-globs
`refs/tags/noctalia-*`), and it happens to match upstream's own `v5.0.0-beta.7`.

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

`hyprland` is the Hyprland Wayland compositor, and it is the one package here that
drags a whole stack in with it. Fedora 44 has no `hyprland` at all, and the nine
libraries it needs are either missing (`aquamarine`, `hyprwire`, `glaze`) or far too
old — Fedora's `hyprutils` is 0.7.1 against a required 0.14.0, its `hyprgraphics`
0.1.5 against 0.5.1. So the whole stack is built here.

**Do not mix ours with Fedora's**, even where Fedora's version technically satisfies
the minimum. Every version in the chain is the one upstream's own `flake.lock`
records for this Hyprland release, because that is the only combination anybody has
actually built and run; a stack assembled from whatever clears the `pkg-config`
floor is a configuration with no testing behind it. `Hyprland --version` prints what
it was built against, which is the quickest way to confirm the set is coherent.

Upstream's Fedora instructions ([discussion
#284](https://github.com/hyprwm/Hyprland/discussions/284)) are useless now — they
date from 2022, when Hyprland was meson and wlroots. It is CMake and its own
`aquamarine` backend today, and none of those `dnf install` lines apply.

Our `hyprutils`, `hyprlang`, `hyprgraphics`, `hyprcursor`, `hyprwayland-scanner-devel`
and `hyprland-protocols-devel` deliberately carry **Fedora's package names and file
paths** so they upgrade Fedora's rather than colliding with them. That is also why
`hyprwayland-scanner-devel` ships a program in a `-devel` package and why its spec,
like `hyprland-protocols`, has no main `%files` section — with no main `%files`,
rpmbuild builds only the subpackage, and no empty base package appears.

Source0 for Hyprland is the **release asset**, `source-v<version>.tar.gz`, not the
autogenerated GitHub archive. It carries the submodules and, more usefully, a
`src/version.h.in` with the git metadata already substituted — so this package needs
no git and cannot pick up *this* repository's tag the way noctalia nearly did.

The awkward part is Lua. Hyprland requires 5.5 with no option to disable it
(`pkg_search_module(LUA REQUIRED ... lua>=5.5 lua<5.6)`), and Fedora 44 has only
5.4.8, so `%build` compiles a static 5.5.1 into the binary. Two details there are
load-bearing, and both look like fussiness until they bite:

- The generated `lua5.5.pc` must use `-L… -llua`, **never** an absolute path to
  `liblua.a`. cmake sorts an absolute library path into the target's link *options*,
  which are emitted before the object files, so the archive gets scanned before
  anything references it and every symbol is dropped — `undefined reference to
  symbol 'lua_pushfstring'` while `liblua.a` sits in plain sight on the link line.
- Lua is compiled `-fvisibility=hidden`. Fedora's libinput links `liblua-5.4.so` for
  its own plugin support and Hyprland links libinput, so both Lua versions share the
  process. Hyprland is built `-rdynamic`, and the executable is searched first when
  the loader resolves a DSO's undefined symbols — so without hidden visibility the
  binary exports 147 `lua_*`/`luaL_*` symbols and libinput's 5.4-compiled calls bind
  to our 5.5 implementation. Nothing triggers it today because Fedora ships no
  libinput plugin directory, but it is a real mismatch waiting for one. Check it with
  `nm -D --defined-only /usr/bin/Hyprland | grep -c ' lua_\| luaL_'`, which must
  print 0.

All of this disappears when the system Lua is 5.5 — rawhide already has it — leaving
a plain `BuildRequires` behind.

**Ten packages, one tag.** `git tag hyprland-<version>-<release>` builds and publishes
the whole stack; the nine libraries are never tagged, and `hyprland.yaml` accepts no
other prefix. A `refs/tags/hyprutils-*` would not build hyprutils on its own anyway —
the build step has no idea which tag fired and always builds all ten — so it would only
be a second name for the same pipeline.

The consequence is worth internalising, because nothing warns you about it: **bumping a
library means bumping `hyprland`'s `Release` too.** The workflow rebuilds Hyprland
whichever library changed, so without that bump the rebuilt binary is published under an
NVR clients already have, and they never receive it. When the library's soname changed,
that is also how you get a stuck upgrade — `dnf` cannot upgrade `hyprutils` while the
installed `hyprland` still requires the old `libhyprutils.so.13`, and the Hyprland built
against the new one is sitting in the repo looking unchanged. So: edit the library's
spec, bump `hyprland`'s `Release`, tag `hyprland`.

Two things are packaged but cannot work yet, and neither is a mistake in the spec:
the `hyprland-uwsm.desktop` session needs `uwsm`, and `hyprland-portals.conf` needs
`xdg-desktop-portal-hyprland` for screen sharing. Fedora 44 has neither. The plain
`hyprland.desktop` session is unaffected; packaging those two here, or building with
`-DNO_UWSM=ON`, are both one-line changes. `hyprpm` is deliberately **not** shipped
(`-DNO_HYPRPM=ON`): it compiles plugins at runtime and would want cmake, meson and a
compiler on every installed system. Plugins can still be built by hand against
`hyprland-devel`.

## Layout

```
.woodpecker/<workflow>.yaml       one workflow per thing you want to build
.github/workflows/build-<x>.yml   the same, being migrated to GitHub Actions
packages/<name>/<name>.spec       one directory per source package
```

> **Migration in progress.** `.woodpecker/` is still the live pipeline and still the
> only thing that publishes into the K3s dnf repo — everything below about building
> and publishing describes it and is still accurate. The four workflows under
> `.github/workflows/` are a translation of it, turned on one at a time by the
> `RPM_BUILD_ENABLED` line at the top of each file:
>
> | Workflow | State |
> | --- | --- |
> | `build-mangowm.yml` | **on** — builds, signs, attaches RPMs to a GitHub Release |
> | `build-hyprland.yml`, `build-noctalia.yml`, `build-fish.yml` | off — start the container, install the toolchain, print the NVRs each spec parses to, then stop |
> | `publish-pages.yml` | on — turns the Releases into a signed dnf repo on GitHub Pages |
>
> `publish-pages.yml` treats the published repo as a **pure function of the set of
> GitHub Releases**: it downloads every release's RPMs, regenerates the metadata from
> scratch and replaces the whole site. Adding a package is publishing a release;
> removing one is deleting a release and re-running the workflow. That is also why
> `repomd.xml` can be signed in the same job that writes it, which is what removes the
> pull-it-back-over-ssh-and-sign step the `.woodpecker/` copies need.
>
> Until the DNS cutover, the two repos are served from different places and both are
> live: `.woodpecker/` publishes to `rpm.<dev-domain>` on K3s, and Actions publishes to
> `https://saeverix.github.io/rpm-builds/`. Client config for the latter is in `repo/`.
>
> **GitHub-side settings that are not in version control**, the counterpart to
> Woodpecker needing **Tag** in *Allowed events*:
>
> - Repository must be **public** — Pages requires it on the Free plan.
> - Settings → Pages → *Build and deployment* → Source: **GitHub Actions**.
> - `RPM_GPG_KEY` repository secret: the armoured private key, same one Woodpecker's
>   `rpm_gpg_key` holds. Export it with
>   `gpg --export-secret-keys --armor <fingerprint>`.
> - Settings → Environments → `github-pages` → *Deployment branches and tags* must
>   allow **tags**, pattern `*`, in addition to the `main` branch rule GitHub creates
>   by default. Publishing is only ever tag-triggered, so without a tag rule the
>   deploy job is rejected by the environment **after a full build has already run** —
>   and merging to `main` does not help, because the ref is still a tag.
>
> Two constraints worth knowing before changing how `publish-pages.yml` is reached.
> A release created by `gh release create` with the default `GITHUB_TOKEN` does **not**
> emit events that start other workflows — GitHub blocks that to stop workflows
> recursing — so a `release: published` trigger silently never fires. And
> `workflow_run` / `workflow_dispatch` only work for workflow files that exist on the
> default branch. That is why the build workflows call `publish-pages.yml` directly
> with `uses:` instead.
>
> Both fire on the same tag, so a tag builds twice until cutover. The GitHub
> workflows also accept a `citest-<package>-*` tag prefix, which matches nothing in
> Woodpecker's `ref:` filters — use it to exercise the GitHub side without
> Woodpecker signing a build and pushing it into the live repo.
>
> Once the migration lands, `.woodpecker/` and this note both go away, along with
> the K3s repo: packages will be published as GitHub Releases and served as a dnf
> repo from GitHub Pages.

Each file in `.woodpecker/` is an independent workflow. Woodpecker runs them in
parallel on separate agents, and each one matches only its own tag prefix, so
tagging one package does not rebuild the others. A package with a build
dependency on another (mangowm on scenefx) just builds both in one workflow and
`dnf install`s the intermediate result.

A workflow that targets more than one distro uses Woodpecker's own `matrix:` rather
than a second file, so the one-workflow-per-package rule still holds. `fish.yaml`
is the only one so far: it defines a `fedora`/`44` axis and an `almalinux`/`10`
axis, each carrying its own `IMAGE`, and interpolates `${IMAGE}` into both steps.
The axes run in parallel and publish into separate repo trees.

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

For a workflow with a `matrix:`, this fallback does not expand it — nothing
interpolates `${IMAGE}` and the axis variables are unset, so the distro
conditionals all silently take the wrong branch. Pick the axis by hand: name its
image on the `podman run` line and pass its variables in. The AlmaLinux axis of
`fish.yaml`:

```sh
podman run --rm -v "$PWD:/w:Z" -w /w \
  -e DISTRO=almalinux -e RELEASEVER=10 \
  quay.io/almalinuxorg/almalinux:10 sh -c '
  dnf -y install python3-pyyaml >/dev/null 2>&1
  python3 - <<PY > /tmp/step.sh
import yaml
print("set -ex")
print("\n".join(yaml.safe_load(open(".woodpecker/fish.yaml"))["steps"][0]["commands"]))
PY
  sh /tmp/step.sh'
```

Both axes need checking before a tag, since either one can fail on its own. Whether
`woodpecker-cli exec` expands a matrix locally, or needs something like
`--matrix DISTRO=...`, is not verified.

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

Cleaning up afterwards: the workflows build as an unprivileged user, and under
rootless podman that leaves `_build` owned by a subuid your account cannot delete.
`rm -rf _build` fails with "Permission denied"; use this instead:

```sh
podman unshare rm -rf _build
```

This used to apply only to fish and noctalia. The GitHub Actions workflows apply it
to every package — see [Conventions](#conventions) — so expect it after any local
run of one of those. The `.woodpecker/` copies still build hyprland and mangowm as
root, so those leave a normally-owned `_build` until cutover.

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
| `fish-4.8.1-1` | `fish` for **both** Fedora 44 and AlmaLinux 10 |
| `mangowm-0.15.6-1` | `mangowm` and `scenefx` |
| `scenefx-0.5.0-1` | `mangowm` and `scenefx` |
| `noctalia-5.0.0-beta.7-1` | `noctalia` |

```sh
git tag fish-4.8.1-1 && git push --tags
```

Tags are matched on `ref` rather than on changed paths, because a path filter is
evaluated against a diff and what a tag diffs against is not worth relying on.

One `fish-*` tag fans out to both distro axes, producing `fish-4.8.1-1.fc44` and
`fish-4.8.1-1.el10`, each published into `/srv/repo/$DISTRO/$RELEASEVER/x86_64`.
**The axes publish independently**, so a tag can end up half-released: if EL10 fails
after Fedora has already pushed, Fedora clients have the new build and EL10 clients
do not. The pipeline goes red, but what already shipped stays shipped. Recovery is
the same as any other failure — fix it, bump `Release`, tag again — which
republishes both. Check both axes are green before calling a release done.

The publish step creates its distro's repo directory (`mkdir -p`) before the first
rsync, because rsync will not create intermediate directories and a brand-new
distro tree does not exist yet. That covers the server side of adding a distro but
not the client side; see the note on the `homelab` repo below.

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
verify instead. `rpm -Kv` behaves the same on EL10's rpm 4.19, so the AlmaLinux axis
needs no special case here.

The same signing key covers both distros, and each repo tree gets its own signed
`repomd.xml` because `createrepo_c` and the pull-back-and-sign both run per axis
against that axis's `$REPO`.

The cluster manifests are **not** in this repo — they live in the `homelab` repo
under `apps/rpm-repo/`, which also serves the client `.repo` file and the public
key. **Adding AlmaLinux needs work there before EL10 clients can install
anything:** `/srv/repo/almalinux/10/` has to be served, and the client `.repo` file
either templated on `$releasever` or split per distro. CI creates the directory and
publishes into it regardless, so a green pipeline does not mean clients can reach
it. Installing on a Fedora box:

```sh
sudo curl -o /etc/yum.repos.d/saeverix.repo https://rpm.<dev-domain>/saeverix.repo
sudo rpm --import https://rpm.<dev-domain>/RPM-GPG-KEY-saeverix
sudo dnf install mangowm fish
```

Woodpecker secrets the publish step needs: `rpm_repo_host`, `rpm_ssh_key`,
`rpm_ssh_known_hosts`, `rpm_gpg_key`.

## Conventions

- **Root does `dnf`; everything else builds as `builder`.** In the GitHub Actions
  workflows, root is used for exactly three things — installing the toolchain,
  `dnf builddep`, and installing a just-built RPM so the next package in a chain can
  link against it. `spectool`, `rpmbuild` and fish's `cargo vendor` all drop
  privileges via `runuser -u builder`, so nothing root-owned ever lands in `_build`;
  each build step asserts that with `find _build ! -user builder`.

  This is not only about tests. `fish` and `noctalia` do need it — six and four of
  their `%check` tests respectively assert on permissions that root bypasses, and
  fish scores 197/203 privileged against 203/203 unprivileged — but the other
  thirteen packages have no `%check` at all and still benefit: root hides packaging
  bugs, because an `%install` that writes outside `%{buildroot}` succeeds silently as
  root and fails loudly as `builder`. Fedora's own mock builds everything as
  `mockbuild` for the same reason. The `.woodpecker/` copies still build hyprland and
  mangowm as root; that difference goes away at cutover.
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
