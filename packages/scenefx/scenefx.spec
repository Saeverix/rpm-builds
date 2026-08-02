# Upstream tags this release "0.5" but meson reports version 0.5.0.
%global tag     0.5
# The library, headers and pkgconfig file are all named after the API version.
%global apiver  0.5

Name:           scenefx
Version:        0.5.0
Release:        1%{?dist}
Summary:        Drop-in replacement for the wlroots scene API adding graphical effects

License:        MIT
URL:            https://github.com/wlrfx/scenefx
Source0:        %{url}/archive/refs/tags/%{tag}/%{name}-%{tag}.tar.gz

BuildRequires:  gcc
BuildRequires:  meson >= 1.3
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(wlroots-0.20) >= 0.20.0
BuildRequires:  pkgconfig(wayland-server) >= 1.24.0
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.41
BuildRequires:  pkgconfig(libdrm) >= 2.4.129
BuildRequires:  pkgconfig(xkbcommon) >= 1.8.0
BuildRequires:  pkgconfig(pixman-1) >= 0.43.0
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(glesv2)
# Optional, enables the colour-management feature.
BuildRequires:  pkgconfig(lcms2)

%description
SceneFX is a drop-in replacement for the wlroots scene API that adds graphical
effects such as rounded corners, blur, shadows and per-surface opacity. It is
used by wlroots-based compositors that want visual effects without having to
reimplement the scene graph themselves.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Headers and pkgconfig file needed to build compositors against %{name}.

%prep
%autosetup -n %{name}-%{tag}

%build
# werror: upstream sets warning_level=2 + werror=true in default_options, which
# turns any warning from a newer GCC than upstream tested with into a hard build
# failure. Never leave this on for a distro build.
# examples: builds the examples/ and tinywl/ demo binaries, none of which are
# installed. Skipping them saves build time and a few extra BuildRequires.
#
# No -Dwrap_mode is needed: upstream already sets wrap_mode=nodownload, so the
# wlroots/libdrm/wayland subproject fallbacks fail loudly instead of reaching
# for the network. Everything resolves from the system packages above.
%meson \
    -Dexamples=false \
    -Dwerror=false
%meson_build

%install
%meson_install

%files
%license LICENSE
%doc README.md
# Upstream calls library() without version/soversion, so there is no
# libscenefx-0.5.so.0 -- the API version lives in the filename and in the
# SONAME. This unversioned .so is therefore the actual runtime library and
# belongs here, not in -devel, even though an unversioned .so outside -devel
# normally means a packaging mistake. Moving it would break every compositor
# linked against it.
%{_libdir}/libscenefx-%{apiver}.so

%files devel
%{_includedir}/scenefx-%{apiver}/
%{_libdir}/pkgconfig/scenefx-%{apiver}.pc

%changelog
* Sun Aug 02 2026 Saeverix - 0.5.0-1
- Initial package, built for MangoWM
