Name:           hyprwire
Version:        0.3.1
Release:        1%{?dist}
Summary:        Wire protocol library for Hyprland IPC

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprwire
Source0:        %{url}/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(hyprutils) >= 0.9.0
BuildRequires:  pkgconfig(libffi)
# For hyprwire-scanner, which parses protocol XML.
BuildRequires:  pkgconfig(pugixml)

%description
hyprwire is the socket and wire-format library behind Hyprland's IPC. Protocols
are described in XML and turned into C++ by the hyprwire-scanner generator that
ships with it. hyprctl talks to a running Hyprland through this library.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Headers, pkgconfig files and the hyprwire-scanner code generator needed to build
against %{name}.

%prep
%autosetup

%build
%cmake -GNinja \
    -DBUILD_TESTING=OFF
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_libdir}/libhyprwire.so.3
%{_libdir}/libhyprwire.so.%{version}

%files devel
# hyprwire-scanner is a build-time code generator, so it belongs with the headers
# rather than in the runtime package -- the same placement Fedora uses for
# hyprwayland-scanner.
%{_bindir}/hyprwire-scanner
%{_includedir}/hyprwire/
%{_libdir}/libhyprwire.so
%{_libdir}/pkgconfig/hyprwire.pc
%{_libdir}/pkgconfig/hyprwire-scanner.pc
%{_libdir}/cmake/hyprwire-scanner/

%changelog
* Wed Aug 05 2026 Saeverix - 0.3.1-1
- Initial package, built for Hyprland
