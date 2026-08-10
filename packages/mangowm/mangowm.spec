Name:           mangowm
Version:        0.15.6
Release:        2%{?dist}
Summary:        Wayland compositor based on wlroots with dwm-like tiling and effects

# mango itself is GPL-3.0-or-later; it carries MIT-licensed code inherited from
# dwl, tinywl, dwm and sway.
License:        GPL-3.0-or-later AND MIT
URL:            https://github.com/mangowm/mango
# Source0:      %%{url}/archive/refs/tags/%%{version}/%%{name}-%%{version}.tar.gz
Source0:        %{url}/archive/8169bfc64746bf76aa92dc692775655d566fbff6.tar.gz

BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(wlroots-0.20) >= 0.20.0
BuildRequires:  pkgconfig(scenefx-0.5) >= 0.5.0
BuildRequires:  pkgconfig(wayland-server) >= 1.23.1
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(libinput) >= 1.27.1
BuildRequires:  pkgconfig(libpcre2-8)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(libcjson)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(libdrm)
# Required by the xwayland feature, which meson_options.txt enables by default.
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(xcb-icccm)

# Do NOT add git here. meson.build shells out to `git rev-parse --short HEAD`
# whenever git is on PATH, and %%{_builddir} is not a git checkout, so the call
# fails and an empty hash gets baked into the -DVERSION= string. With git
# absent, meson.build takes its clean fallback branch and VERSION becomes
# "%%{version}(unknown)". The same applies to the CI image -- see
# .woodpecker/mangowm.yaml.

# Built with -DXWAYLAND, so the X server is needed at runtime.
Requires:       xorg-x11-server-Xwayland

%description
Mango is a Wayland compositor built on wlroots and SceneFX. It follows the
dwl/dwm model of dynamic tiling with tags, and adds animations, rounded corners,
blur and shadows on top. Configuration is a plain text file at
/etc/mango/config.conf, and the mmsg tool talks to a running instance over IPC.

%prep
# The package is named mangowm (matching Terra and other repos), but the GitHub
# archive unpacks into the repo name, mango-%%{version}.
%autosetup -n mango-8169bfc64746bf76aa92dc692775655d566fbff6

%build
%meson
%meson_build

%install
%meson_install

%files
%license LICENSE
%doc README.md docs
%{_bindir}/mango
%{_bindir}/mmsg
%{_mandir}/man1/mmsg.1*
%{_datadir}/wayland-sessions/mango.desktop
%{_datadir}/xdg-desktop-portal/mango-portals.conf
%dir %{_sysconfdir}/mango
# noreplace: this is the live keybinding and layout config. An upgrade that
# overwrites it would silently throw away the user's whole setup.
%config(noreplace) %{_sysconfdir}/mango/config.conf

%changelog
* Mon Aug 03 2026 Saeverix - 0.15.6-1
- Bumped to 0.15.6

* Sun Aug 02 2026 Saeverix - 0.15.5-1
- Initial package
