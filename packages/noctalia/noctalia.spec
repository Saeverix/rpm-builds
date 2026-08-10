# Upstream tags v5 betas as v5.0.0-beta.7, which RPM cannot use verbatim: a
# hyphen is the Version-Release separator. Version therefore uses a tilde, which
# sorts BELOW everything, so the eventual 5.0.0 final upgrades cleanly with no
# epoch. %%{upstream_version} keeps the hyphenated form for the tag URL and the
# unpack directory. Bumping a beta means editing both lines.
%global upstream_version 5.0.0-beta.8

Name:           noctalia
Version:        5.0.0~beta.8
Release:        1%{?dist}
# Verbatim from upstream's PACKAGING.md, which asks packagers not to substitute a
# shorter blurb ("lightweight Wayland bar", "status bar"). Noctalia is a full
# desktop shell, not a bar.
Summary:        A sleek, customizable desktop shell crafted for Wayland

# Noctalia itself is MIT. third_party/ vendors code that is statically linked
# into the binary: Wuffs (Apache-2.0 OR MIT), Material Color Utilities
# (Apache-2.0), Luau (MIT) and fzy (MIT).
License:        MIT AND Apache-2.0
URL:            https://github.com/noctalia-dev/noctalia
Source0:        %{url}/archive/refs/tags/v%{upstream_version}/%{name}-%{upstream_version}.tar.gz

# C++23 is mandatory (GCC 13+); Fedora 44 ships GCC 16.
BuildRequires:  gcc-c++
BuildRequires:  meson
BuildRequires:  ninja-build

BuildRequires:  pkgconfig(sdbus-c++)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(wayland-egl)
BuildRequires:  pkgconfig(wayland-scanner)
# There is no Qt or GTK here: the UI is Wayland plus OpenGL ES. Both of these
# come from libglvnd-devel on Fedora 44. Upstream's README lists libEGL-devel and
# mesa-libGLES-devel, which are not package names Fedora 44 has -- asking for the
# pkg-config names instead is what makes this resolve. meson.build falls back to
# libepoxy when EGL/GLES are missing; that fallback is not needed here.
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(cairo-ft)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(pangoft2)
BuildRequires:  pkgconfig(harfbuzz)
BuildRequires:  pkgconfig(librsvg-2.0)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gobject-2.0)
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(libsecret-1) >= 0.20
BuildRequires:  pkgconfig(libsodium) >= 1.0.18
BuildRequires:  pkgconfig(polkit-agent-1)
BuildRequires:  pkgconfig(polkit-gobject-1)
BuildRequires:  pkgconfig(libpipewire-0.3)
# meson.build asks for wireplumber-0.5 specifically. 0.4 is not enough.
BuildRequires:  pkgconfig(wireplumber-0.5)
BuildRequires:  pkgconfig(libcurl)
BuildRequires:  pkgconfig(libqalculate)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(md4c)
BuildRequires:  pkgconfig(nlohmann_json)
BuildRequires:  pkgconfig(tomlplusplus)
BuildRequires:  pkgconfig(libical)
BuildRequires:  pkgconfig(libwebp)
BuildRequires:  pkgconfig(libjxl)
BuildRequires:  pkgconfig(libjxl_threads)
BuildRequires:  pkgconfig(sndfile)
# No .pc file: meson.build reaches these through cc.find_library / cc.has_header.
# Fedora splits stb into one package per header, and both ship the stb/-prefixed
# path (/usr/include/stb/stb_image_resize2.h) that meson checks for. Older stb
# packaging that only had stb_image_resize fails the configure check.
BuildRequires:  pam-devel
BuildRequires:  stb_image_resize2-devel
BuildRequires:  stb_image_write-devel
BuildRequires:  jemalloc-devel
# For desktop-file-validate in %%check.
BuildRequires:  desktop-file-utils

# Libraries alone are not enough for audio, the volume OSD, privacy indicators
# and the spectrum -- those features need the daemons running.
Requires:       pipewire
Requires:       wireplumber
# Plugin git sources and plugin auto-update invoke git on PATH.
Requires:       git-core

Recommends:     upower
Recommends:     ddcutil

# No Conflicts against mako, dunst, swaync or a waybar tray host. On non-Plasma
# sessions Noctalia claims org.freedesktop.Notifications and
# org.kde.StatusNotifierWatcher, so those must not RUN alongside it -- but they
# can be installed side by side, and Conflicts would block that for no reason.
#
# No hard Requires on a Secret Service provider either. One is recommended for
# credential and encrypted-state persistence, but which of gnome-keyring,
# kwallet or keepassxc fits depends on the session, and libsecret (pulled in as a
# library dependency) is only the client side.

%description
Noctalia is a desktop shell for Wayland: bars, dock, launcher, notifications,
lock screen, wallpaper and a settings UI in one binary. It is written in C++
against Wayland and OpenGL ES directly, with no Qt or GTK involved.

Start it from a compositor autostart entry or the shipped desktop file, both of
which run "noctalia --daemon", and control a running instance with
"noctalia msg ...".

# rpm sizes the compile job count as MemTotal / %%{_smp_tasksize_proc}, capped at
# nproc, and the default assumes 512 MiB per compiler process. This tree needs
# roughly three times that: measured peak cc1plus RSS is 1.37 GiB (worst offender
# src/app/application.cpp -- a 10 KiB file whose headers expand to 1.46M lines of
# assembly), and a -j16 compile peaks at 11.1 GiB resident across the tree. So on
# any builder with less than nproc * 1.4 GiB the OOM killer takes cc1plus, and
# because %%optflags carry -pipe the corpse reaches the assembler as a truncated
# stream -- it reports "unknown pseudo-op", "end of file not at end of a line" and
# "open CFI at the end of file" rather than anything mentioning memory. Do not
# chase those; they are the symptom.
#
# Raising the assumed task size is the whole fix, and it scales with the builder
# rather than hardcoding a -j number: 15 jobs on a 32 GiB machine, 4 on 8 GiB, 2
# on 4 GiB. It applies to %%check too, which rebuilds before running the tests.
# LTO is NOT implicated, which is worth recording because it is the obvious
# suspect: dropping -ffat-lto-objects moves peak RSS only from 1.22 to 1.09 GiB
# on the worst file, so %%_lto_cflags is left alone. The LTO link step's own peak
# was never measured -- if a future build dies at [867/867] instead of mid-compile
# that is a different ceiling, and this macro will not move it.
#
# CAVEAT for CI: this reads /proc/meminfo, which inside a container reports the
# HOST's memory and not the cgroup limit. If the Woodpecker pod is capped below
# what the node advertises, rpm cannot see it and this macro will still overshoot.
# The ceiling then has to be stated outright, as an explicit
# --define '_smp_build_ncpus N' on the rpmbuild line in .woodpecker/noctalia.yaml.
%global _smp_tasksize_proc 2048

%prep
%autosetup -n %{name}-%{upstream_version}

%build
# git IS on PATH for this build, because the plugin_git_export test in %%check
# drives real repositories. That means meson's vcs_tag() takes its git branch and
# actually runs `git describe` rather than the no-git fallback -- and that search
# walks UP out of %%{_builddir} into whatever repository the build tree happens to
# sit inside. In CI that is this rpm-builds checkout, which answers with its own
# tag (verified: "fish-4.8.1-1-dirty") and would bake it into the binary as
# noctalia's revision. The ceiling stops the walk, so `git describe` fails and
# vcs_tag substitutes its declared "unknown" fallback, which is what upstream
# intends for a tarball build. Do not swap this for GIT_DIR: that suppresses
# discovery everywhere and breaks the test's own repositories.
export GIT_CEILING_DIRECTORIES=%{_builddir}

# Tests are off by default in anything but a debug build, so %%check needs them
# asked for explicitly. jemalloc is upstream's recommendation on glibc; the
# default "auto" would silently drop it if jemalloc-devel ever went missing.
#
# -Dnative_optimizations stays off: upstream forbids it for distro packages
# because it emits CPU-local codegen. Fedora's %%meson also configures
# --buildtype=plain rather than upstream's suggested release, so that %%optflags
# apply -- the only loss is meson's release-only -ffunction-sections and
# -Wl,--gc-sections, which affect size and not behaviour.
%meson -Dtests=enabled -Djemalloc=enabled
%meson_build

%install
%meson_install

%check
# Needed here as well as in %%build: `meson test` rebuilds before running, and
# vcs_tag reruns on every build, so dropping the ceiling here would let the wrong
# revision back in.
export GIT_CEILING_DIRECTORIES=%{_builddir}
%meson_test
desktop-file-validate %{buildroot}%{_datadir}/applications/dev.noctalia.Noctalia.desktop

%files
%license LICENSE
%doc README.md PACKAGING.md CREDITS.md
%{_bindir}/noctalia
# Required at runtime, not documentation. The assets tree carries the fonts,
# translations, theme templates, glyph maps and sounds; shipping only the binary
# breaks all of them.
%{_datadir}/noctalia/
%{_datadir}/applications/dev.noctalia.Noctalia.desktop
%{_datadir}/icons/hicolor/scalable/apps/noctalia.svg
# Nothing else to list: upstream ships no systemd unit, no man page and no
# AppStream metainfo. The hicolor icon needs no cache scriptlets -- Fedora
# handles that with file triggers.

%changelog
* Tue Aug 04 2026 Saeverix - 5.0.0~beta.7-1
- Initial package
