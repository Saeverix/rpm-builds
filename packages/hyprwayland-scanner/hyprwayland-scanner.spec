Name:           hyprwayland-scanner
Version:        0.4.6
Release:        1%{?dist}
Summary:        Wayland protocol scanner that emits C++ instead of C

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprwayland-scanner
Source0:        %{url}/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(pugixml)

%description
hyprwayland-scanner turns Wayland protocol XML into C++ glue, in place of the C
that the reference wayland-scanner emits. It runs at build time only; aquamarine
and Hyprland both generate their protocol code with it.

# Fedora 44 has 0.4.2, too old for the aquamarine and Hyprland versions this repo
# builds, so we ship our own -- and it has to land on exactly the same paths, or
# dnf hits a file conflict instead of doing an upgrade. Fedora puts the generator,
# its pkgconfig file and its CMake config all in hyprwayland-scanner-devel and
# builds no base package at all, which is odd for something that is really a
# program, but matching it is what makes the upgrade clean.
#
# This spec therefore has no main %%files section on purpose: rpmbuild then builds
# only the subpackage below, with no empty hyprwayland-scanner package alongside
# it.
%package        devel
Summary:        Wayland protocol C++ code generator, used to build Hyprland

%description    devel
The hyprwayland-scanner generator, plus the pkgconfig and CMake files that let a
project find it.

%prep
%autosetup

%build
%cmake -GNinja
%cmake_build

%install
%cmake_install

%files devel
%license LICENSE
%doc README.md
%{_bindir}/hyprwayland-scanner
%{_libdir}/pkgconfig/hyprwayland-scanner.pc
%{_libdir}/cmake/hyprwayland-scanner/

%changelog
* Wed Aug 05 2026 Saeverix - 0.4.6-1
- Initial package, built for Hyprland
