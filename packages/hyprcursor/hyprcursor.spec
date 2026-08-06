Name:           hyprcursor
Version:        0.1.13
Release:        1%{?dist}
Summary:        Hyprland cursor theme format library and utility

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprcursor
Source0:        %{url}/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(hyprlang) >= 0.4.2
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(librsvg-2.0)
BuildRequires:  pkgconfig(libzip)
BuildRequires:  pkgconfig(tomlplusplus)

%description
hyprcursor implements the Hyprland cursor theme format, which stores cursors as
SVG and renders them at the size the compositor asks for instead of shipping one
bitmap per size. The hyprcursor-util tool creates and extracts theme archives.

# Fedora 44 has 0.1.11 and Hyprland only asks for >= 0.1.7, so this rebuild is not
# strictly forced -- but 0.1.13 is the version upstream's flake.lock pins for
# Hyprland 0.56.1, and the point of this chain is to ship the combination upstream
# actually tests.
%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Headers and pkgconfig file needed to build against %{name}.

%prep
%autosetup

%build
%cmake -GNinja \
    -DBUILD_TESTING=OFF \
    -DINSTALL_TESTS=OFF
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_bindir}/hyprcursor-util
%{_libdir}/libhyprcursor.so.0
%{_libdir}/libhyprcursor.so.%{version}

%files devel
%{_includedir}/hyprcursor/
# Installed alongside the directory above, as the target's PUBLIC_HEADER. Fedora's
# 0.1.11 ships it too, so dropping it would break anything that includes
# <hyprcursor.hpp> rather than <hyprcursor/hyprcursor.hpp>.
%{_includedir}/hyprcursor.hpp
%{_libdir}/libhyprcursor.so
%{_libdir}/pkgconfig/hyprcursor.pc

%changelog
* Wed Aug 05 2026 Saeverix - 0.1.13-1
- Initial package, built for Hyprland
