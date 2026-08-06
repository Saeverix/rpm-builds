Name:           hyprlang
Version:        0.6.8
Release:        1%{?dist}
Summary:        Configuration language library used by the Hyprland ecosystem

# Unlike the rest of the hypr* libraries, which are BSD-3-Clause, hyprlang is
# LGPL. This matches Fedora's own License field for the package.
License:        LGPL-3.0-only
URL:            https://github.com/hyprwm/hyprlang
Source0:        %{url}/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(hyprutils) >= 0.7.1

%description
hyprlang implements the configuration language shared by Hyprland and its
satellite projects: variables, keywords, categories, sourcing and live reload.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Headers and pkgconfig file needed to build against %{name}.

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
# Same soname as Fedora's 0.6.4, which is why Fedora's hyprcursor keeps working
# while this upgrade is in flight. We rebuild hyprcursor anyway.
%{_libdir}/libhyprlang.so.2
%{_libdir}/libhyprlang.so.%{version}

%files devel
# Upstream installs one flat header rather than a directory.
%{_includedir}/hyprlang.hpp
%{_libdir}/libhyprlang.so
%{_libdir}/pkgconfig/hyprlang.pc

%changelog
* Wed Aug 05 2026 Saeverix - 0.6.8-1
- Initial package, built for Hyprland
