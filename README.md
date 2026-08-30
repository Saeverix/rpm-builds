# rpm-builds

RPM spec files for tools that are not in the Fedora repositories, or that Fedora
ships too old, built by GitHub Actions. Targets **Fedora 44** and **AlmaLinux 10**,
x86_64.

## Packages

| Package | Version | Workflow | Targets | Upstream |
| --- | --- | --- | --- | --- |
| `scenefx`, `scenefx-devel` | 0.5.0 (tag `0.5`) | `mangowm` | fc44 | <https://github.com/wlrfx/scenefx> |
| `mangowm` | 0.16.1 | `mangowm` | fc44 | <https://github.com/mangowm/mango> |
| `fish` | 4.8.1 | `fish` | fc44, el10 | <https://github.com/fish-shell/fish-shell> |
| `noctalia` | 5.0.0~beta.8 | `noctalia` | fc44 | <https://github.com/noctalia-dev/noctalia> |
| `ghostty` | 1.3.1 | `ghostty` | fc44 | <https://github.com/ghostty-org/ghostty> |
| `hyprwayland-scanner-devel` | 0.4.6 | `hyprland` | fc44 | <https://github.com/hyprwm/hyprwayland-scanner> |
| `hyprland-protocols-devel` | 0.7.0 | `hyprland` | fc44 | <https://github.com/hyprwm/hyprland-protocols> |
| `glaze-devel` | 7.2.0 | `hyprland` | fc44 | <https://github.com/stephenberry/glaze> |
| `hyprutils`, `hyprutils-devel` | 0.14.0 | `hyprland` | fc44 | <https://github.com/hyprwm/hyprutils> |
| `hyprlang`, `hyprlang-devel` | 0.6.8 | `hyprland` | fc44 | <https://github.com/hyprwm/hyprlang> |
| `hyprwire`, `hyprwire-devel` | 0.3.1 | `hyprland` | fc44 | <https://github.com/hyprwm/hyprwire> |
| `hyprgraphics`, `hyprgraphics-devel` | 0.5.1 | `hyprland` | fc44 | <https://github.com/hyprwm/hyprgraphics> |
| `hyprcursor`, `hyprcursor-devel` | 0.1.13 | `hyprland` | fc44 | <https://github.com/hyprwm/hyprcursor> |
| `aquamarine`, `aquamarine-devel` | 0.14.0 | `hyprland` | fc44 | <https://github.com/hyprwm/aquamarine> |
| `hyprland`, `hyprland-devel` | 0.56.2 | `hyprland` | fc44 | <https://github.com/hyprwm/Hyprland> |

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

`ghostty` is the GPU-accelerated terminal emulator, and Fedora does not package it
at all. It is built with Zig, and that is the whole reason this package looks
different from everything else here: `build.zig.zon` pins `minimum_zig_version`
to 0.15.2, Fedora 44 ships Zig 0.16.0, and upstream's `main` branch only gained
0.16 compatibility after the v1.3.1 tag -- there are real breaking changes
between the two, so building against the system Zig is not safe. Rather than
wait on a Fedora Zig bump or track upstream `main`, the spec vendors an official
Zig 0.15.2 release tarball as `Source2` and uses it purely as a build-time tool:
extracted, put on `PATH` for `%install`, and never installed as a system package
or linked into anything.

Source0 has to be the **release tarball**
(`https://release.files.ghostty.org/1.3.1/ghostty-1.3.1.tar.gz`), not GitHub's
autogenerated archive. Upstream's own `PACKAGING.md` is explicit about this: the
release tarball is preprocessed to cut the build-time dependency list, and it is
signed -- with minisign, not GPG, so `%prep` cannot use the `%{gpgverify}` macro
the way fish.spec does. There is no rpm macro for minisign either, so it is a
plain shell command with upstream's public key given directly on the command
line; no keyring file is needed. Read `PACKAGING.md` at the matching tag when
bumping this package -- it says outright that it is only accurate for the
version alongside it.

The build itself follows upstream's own two-step packaging flow. First,
`nix/build-support/fetch-zig-cache.sh` reads `build.zig.zon.txt` (one dependency
URL per line, including a `git+https://` one) and runs `zig fetch` on each into
a cache directory -- the only step that touches the network, and the only
reason `build-ghostty.yml` installs `git-core` at all. Second, `zig build
--system <cache>/p` builds entirely offline, dynamically linking every C-library
dependency Fedora ships (GTK4, libadwaita, harfbuzz, oniguruma, pixman, and so
on) against the system copy, while building the libraries Fedora doesn't carry
(highway, wuffs, spirv-cross, glslang, sentry, breakpad) and the pure-Zig
dependencies from the fetched cache. `build-ghostty.yml` runs the fetch step and
hands the resulting cache as `Source3`, a bare filename with no URL -- exactly
like fish's vendored cargo crates -- so `spectool` skips it and `%build` never
reaches the network. `zig build` also fuses "build" and "install" into one step
once `--prefix`/`DESTDIR` are given, so the actual compile happens in `%install`
rather than `%build`.

Two things worth knowing if this ever needs debugging: `zig build` installs
libraries to `$prefix/lib` rather than Fedora's `lib64`, which
`--prefix-lib-dir %{_libdir}` corrects for `libghostty-vt.so` -- but the
`.pc` file's destination is hardcoded upstream to `share/pkgconfig`, unaffected
by that flag, and is left there rather than "fixed" because pkgconf's default
search path already includes `/usr/share/pkgconfig`. And Ghostty unconditionally
installs a Nautilus (GNOME Files) right-click extension -- it is a plain file
copy with no dependency on `nautilus-python` being present at build time, not
something that only appears when its build dependency is available. Arch's
PKGBUILD carves the terminfo, shell integration and this Nautilus extension out
into three extra subpackages; none of that is replicated here. Everything
except the Nautilus extension ships in one `ghostty` package, matching how this
repo avoids subpackages without a concrete reason (see `hyprwayland-scanner-devel`
below), and the Nautilus extension is simply deleted from `%{buildroot}` in
`%install` instead of being split out.

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

That pinning is looser than it sounds, and the exact rule matters when bumping.
`flake.lock` records **commits, not tags** — for Hyprland 0.56.2 only
`hyprwayland-scanner` sits exactly on a release (`v0.4.6`); every other input points
at an untagged commit somewhere after one. So the rule here is: ship each library's
**newest release at or before the commit that Hyprland's `flake.lock` pins**. That
keeps us on tarballs RPM can name, while never getting ahead of a combination
upstream has built.

Two consequences that make "bump everything to its latest release" the wrong move,
both recorded next to the `Version:` line in the spec they apply to:

- **glaze must stay on 7.x.** Hyprland asks for `find_package(glaze 7...<8)`, so
  glaze 8 is excluded by upstream's own range.
- **hyprutils stays at 0.14.0** even though 0.14.1 exists, because 0.56.2's pinned
  commit predates 0.14.1. It is the only library where newest-release and
  what-upstream-tested currently disagree — everywhere else the pinned commit sits
  *ahead* of the tag we ship, so the newest release is also the right one.

Re-derive both when bumping Hyprland; neither is a permanent fact.

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
.github/workflows/build-<name>.yml   one workflow per thing you want to build
.github/workflows/publish-pages.yml  turns GitHub Releases into the dnf repo
packages/<name>/<name>.spec          one directory per source package
repo/                                client-facing files served alongside the repo
```

`publish-pages.yml` treats the published repo as a **pure function of the set of
GitHub Releases**: it downloads every release's RPMs, regenerates the metadata from
scratch and replaces the whole site. Adding a package is publishing a release;
removing one is deleting a release and re-running the workflow. That is also why
`repomd.xml` can be signed in the same job that writes it — there is no separate
server to pull a generated file back from before it can be signed.

The repo is served from GitHub Pages under the custom domain `rpm.vries.cloud`
(a CNAME plus GitHub's own Pages custom-domain setting). Client config for it is
in `repo/`.

**GitHub-side settings that are not in version control:**

- Repository must be **public** — Pages requires it on the Free plan.
- Settings → Pages → *Build and deployment* → Source: **GitHub Actions**.
- Settings → Pages → *Custom domain*: `rpm.vries.cloud`, plus the matching CNAME
  record with the DNS provider.
- `RPM_GPG_KEY` repository secret: the armoured private key. Export it with
  `gpg --export-secret-keys --armor <fingerprint>`.
- Settings → Environments → `github-pages` → *Deployment branches and tags* must
  allow **tags**, pattern `*`, in addition to the `main` branch rule GitHub creates
  by default. Publishing is only ever tag-triggered, so without a tag rule the
  deploy job is rejected by the environment **after a full build has already run** —
  and merging to `main` does not help, because the ref is still a tag.

Two constraints worth knowing before changing how `publish-pages.yml` is reached.
A release created by `gh release create` with the default `GITHUB_TOKEN` does **not**
emit events that start other workflows — GitHub blocks that to stop workflows
recursing — so a `release: published` trigger silently never fires. And
`workflow_run` / `workflow_dispatch` only work for workflow files that exist on the
default branch. That is why the build workflows call `publish-pages.yml` directly
with `uses:` instead.

Each `build-<name>.yml` is an independent workflow. GitHub Actions runs them
concurrently, and each one matches only its own tag prefix (via its `on.push.tags`
filter), so tagging one package does not rebuild the others. A package with a build
dependency on another (mangowm on scenefx) just builds both in one workflow and
`dnf install`s the intermediate result.

A workflow that targets more than one distro uses GitHub Actions' own
`strategy.matrix` rather than a second file, so the one-workflow-per-package rule
still holds. `build-fish.yml` is the only one so far: it defines a `fedora`/`44`
axis and an `almalinux`/`10` axis, each carrying its own container `image`, and
runs both as parallel jobs feeding a single release job.

There is no build script and no ordering file — ordering is the order of the
steps in a workflow, and dependencies are whatever that workflow installs.

## Adding a package

1. `packages/<name>/<name>.spec`
2. `.github/workflows/build-<name>.yml` — copy an existing one (`build-mangowm.yml`
   for a simple single-distro package) and change the spec paths and the tag
   prefix in `on.push.tags` and `on.pull_request.paths`.

## Building locally

Publishing is tag-triggered only, so this is where a spec gets verified before it
is tagged — a build error found here costs nothing, whereas one found in CI costs
a `Release` bump and a second tag. A plain PR against `main` also runs the build
job (without signing or publishing), so a spec gets real CI feedback before a tag
even without a local run — but a local run is faster to iterate on.

The CI definition is the build definition, so run it by extracting the workflow's
own steps and running them in a container, with the workspace bind-mounted so the
RPMs survive. This pulls the `prepare build environment` and `build` steps' `run:`
blocks out of the YAML and feeds them to one shell — change the filename to pick a
different package:

```sh
podman run --rm -v "$PWD:/w:Z" -w /w registry.fedoraproject.org/fedora:44 sh -c '
  dnf -y install python3-pyyaml >/dev/null 2>&1
  python3 - <<PY > /tmp/steps.sh
import yaml
steps = yaml.safe_load(open(".github/workflows/build-mangowm.yml"))["jobs"]["build"]["steps"]
print("set -ex")
for name in ("prepare build environment", "build"):
    print(next(s for s in steps if s.get("name") == name)["run"])
PY
  sh /tmp/steps.sh'
```

For a workflow with a `strategy.matrix` (only `build-fish.yml` today), this does
not expand the matrix — nothing sets `image` or the job-level `DISTRO` env var, so
the distro conditionals inside the step would silently take the wrong branch. Pick
the axis by hand: name its image on the `podman run` line and pass `DISTRO` in as
a container env var. The AlmaLinux axis:

```sh
podman run --rm -v "$PWD:/w:Z" -w /w \
  -e DISTRO=almalinux \
  quay.io/almalinuxorg/almalinux:10 sh -c '
  dnf -y install python3-pyyaml >/dev/null 2>&1
  python3 - <<PY > /tmp/steps.sh
import yaml
steps = yaml.safe_load(open(".github/workflows/build-fish.yml"))["jobs"]["build"]["steps"]
print("set -ex")
for name in ("prepare build environment", "build"):
    print(next(s for s in steps if s.get("name") == name)["run"])
PY
  sh /tmp/steps.sh'
```

Both axes need checking before a tag, since either one can fail on its own.

**Do not hand-copy the commands into a script instead.** Each `run: |` block is
fed to one shell as-is, so state (installed packages, exported variables, `_build`
contents) leaks between its lines by design; a transcription that drifted from the
YAML by a single `cd` is exactly how a working-directory bug once reached CI while
passing locally. Extracting and running the actual YAML is the only faithful test.

**Do not start a second `:Z` container against this directory while a build is
running.** `:Z` relabels the bind mount with the *calling* container's SELinux MCS
category, so a second container silently steals the label out from under the first
one and every file the running build touches from then on fails. It does not look
like a permission problem either: the symptoms are hundreds of
`as: BFD ... assertion fail`, a bogus `No space left on device` on a disk with
600 GB free, and `Permission denied` in a directory that has already accepted
hundreds of object files. If you want to inspect or validate something mid-build,
either wait, or mount read-only (`:z,ro`) — a shared label does not get stolen.

Cleaning up afterwards: every workflow builds `rpmbuild` as an unprivileged
`builder` user (see [Conventions](#conventions)), and under rootless podman that
leaves `_build` owned by a subuid your account cannot delete. `rm -rf _build`
fails with "Permission denied"; use this instead:

```sh
podman unshare rm -rf _build
```

## Publishing

**A tag is the only thing that signs, releases and publishes.** A plain push to
`main` builds nothing (no trigger matches it), and a pull request or manual
`workflow_dispatch` runs the build job — so a spec gets real feedback — but skips
the `sign`/`release` steps and never touches `publish-pages.yml`. So a tag always
ends in a publish, and the spec should be checked via a PR or a local run (see
[Building locally](#building-locally)) before it is tagged.

Tag names decide what publishes, and the prefix must match the workflow's
`on.push.tags` filter:

| Tag | Publishes |
| --- | --- |
| `fish-4.8.1-1` | `fish` for **both** Fedora 44 and AlmaLinux 10 |
| `mangowm-0.15.6-1` | `mangowm` and `scenefx` |
| `scenefx-0.5.0-1` | `mangowm` and `scenefx` |
| `noctalia-5.0.0-beta.7-1` | `noctalia` |
| `hyprland-0.56.2-1` | `hyprland` and the nine libraries it needs |
| `ghostty-1.3.1-1` | `ghostty` |

```sh
git tag fish-4.8.1-1 && git push --tags
```

Tags are matched on `ref` rather than on changed paths, because a path filter is
evaluated against a diff and what a tag diffs against is not worth relying on.

One `fish-*` tag fans out to both distro axes as separate matrix jobs, producing
`fish-4.8.1-1.fc44` and `fish-4.8.1-1.el10`. Both axes feed a single `release` job
that runs only once both have succeeded, so a tag cannot end up half-released —
either both RPMs land on the GitHub Release, or neither does.

If a tagged build fails, fix the spec and tag again with `Release` bumped — e.g.
`mangowm-0.15.6-2`. Prefer a new tag over force-pushing the existing one: a moved
tag no longer identifies what is in the repo, even though GitHub Actions itself
will happily rebuild on a force-pushed tag.

Only binary RPMs are published. `-debuginfo`, `-debugsource` and the SRPM are
filtered out at upload time — they are all rebuildable from the tagged spec. The
repo keeps the newest three builds of each package; older ones are pruned by `dnf
repomanage` in `publish-pages.yml` before the metadata is regenerated.

Everything is GPG-signed with the single `RPM_GPG_KEY` repository secret, and the
private key never leaves the job that uses it. Each `build-<name>.yml`'s `sign`
step signs the individual RPMs right after they are built, so the GitHub Release
asset is byte for byte what dnf serves. `publish-pages.yml` separately imports the
same secret to sign each distro tree's `repomd.xml` in the very job that generates
it with `createrepo_c` — there is no remote signing step, because nothing here
runs outside GitHub's own runners. Clients get both `gpgcheck=1` and
`repo_gpgcheck=1`.

Do not verify the signing with a `%{SIGPGP}` tag check. That is the legacy
signature tag and reads `(none)` on rpm 4.20 even for a correctly signed package,
so it rejects every build; the sign steps import the public key and let `rpm -Kv`
verify instead. `rpm -Kv` behaves the same on EL10's rpm 4.19, so the AlmaLinux
axis needs no special case here.

The same signing key covers both distros, and `publish-pages.yml` signs each
distro tree's `repomd.xml` separately, in the same loop that runs `createrepo_c`
over it.

The client-facing files are checked into this repo, under `repo/`:
`saeverix.repo`, `saeverix-almalinux.repo`, `index.html` and the committed public
key `RPM-GPG-KEY-saeverix`. `publish-pages.yml` copies the first three into the
generated site as-is and cross-checks the committed public key's fingerprint
against the one it just signed with, so the two cannot silently drift apart.
Installing on a Fedora box:

```sh
sudo curl -o /etc/yum.repos.d/saeverix.repo https://rpm.vries.cloud/saeverix.repo
sudo rpm --import https://rpm.vries.cloud/RPM-GPG-KEY-saeverix
sudo dnf install mangowm fish
```

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
  fourteen packages have no `%check` at all and still benefit: root hides packaging
  bugs, because an `%install` that writes outside `%{buildroot}` succeeds silently as
  root and fails loudly as `builder`. Fedora's own mock builds everything as
  `mockbuild` for the same reason.
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
