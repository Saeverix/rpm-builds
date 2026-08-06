# Nothing here is compiled, so there is no ELF for rpm to extract debuginfo from.
# Without this, rpm still generates a debugsource package and then fails the build
# with "Empty %%files file ... debugsourcefiles.list".
%global debug_package %{nil}

Name:           hyprland-protocols
Version:        0.7.0
Release:        1%{?dist}
Summary:        Wayland protocol extensions for Hyprland

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprland-protocols
Source0:        %{url}/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  meson >= 0.60.3
BuildRequires:  ninja-build
# No compiler: the meson project() call declares no languages, because the whole
# package is XML plus a pkgconfig file.

%description
The Wayland protocol extensions Hyprland implements, as XML: toplevel export and
mapping, global shortcuts, focus grab, CTM control, surface, lock notify and
input capture. Compositors and clients generate their own bindings from these
files, so the package carries no code of its own.

# Fedora 44 has 0.7.0's predecessor 0.4.0, which ships only four of the eight
# protocols -- Hyprland 0.56 generates code from all eight, so this package is not
# optional. As with hyprwayland-scanner, Fedora builds a -devel package and no base
# package, and we install on the same paths, so this spec has no main %%files
# section and produces only the subpackage below.
%package        devel
Summary:        Hyprland Wayland protocol XML files
BuildArch:      noarch

%description    devel
The protocol XML files and the hyprland-protocols pkgconfig file, which exports
their location as pkgdatadir.

%prep
%autosetup

%build
%meson
%meson_build

%install
%meson_install

%files devel
%license LICENSE
%doc README.md
%{_datadir}/hyprland-protocols/
%{_datadir}/pkgconfig/hyprland-protocols.pc

%changelog
* Wed Aug 05 2026 Saeverix - 0.7.0-1
- Initial package, built for Hyprland
