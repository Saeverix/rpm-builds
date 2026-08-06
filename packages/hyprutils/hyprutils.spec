Name:           hyprutils
Version:        0.14.0
Release:        1%{?dist}
Summary:        Utility library for the Hyprland ecosystem

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprutils
Source0:        %{url}/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(pixman-1)

%description
hyprutils carries the pieces every Hyprland project needs: math and geometry
types, string helpers, memory ownership wrappers, an animation framework and OS
utilities. Hyprland, hyprlang, hyprwire, hyprgraphics and aquamarine all build
against it.

# Fedora 44 has 0.7.1, which is libhyprutils.so.6; this is libhyprutils.so.13, so
# the upgrade drops the old soname. Nothing in Fedora 44 links so.6 except
# hyprlang, hyprgraphics and hyprutils-devel, and this repo rebuilds all of those
# against 0.14.0 in the same workflow, so the set stays consistent.
%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Headers and pkgconfig file needed to build against %{name}.

%prep
%autosetup

%build
# Upstream adds -O3 of its own on top of %%optflags for any build type that is not
# Debug, which is what an install from source gets too. Leave it.
%cmake -GNinja \
    -DBUILD_TESTING=OFF
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_libdir}/libhyprutils.so.13
%{_libdir}/libhyprutils.so.%{version}

%files devel
%{_includedir}/hyprutils/
%{_libdir}/libhyprutils.so
%{_libdir}/pkgconfig/hyprutils.pc

%changelog
* Wed Aug 05 2026 Saeverix - 0.14.0-1
- Initial package, built for Hyprland
