Name:           aquamarine
Version:        0.13.0
Release:        1%{?dist}
Summary:        Rendering and backend library for Wayland compositors

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/aquamarine
Source0:        %{url}/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(hyprutils) >= 0.8.0
BuildRequires:  pkgconfig(libseat) >= 0.8.0
BuildRequires:  pkgconfig(libinput) >= 1.26.0
BuildRequires:  pkgconfig(libdisplay-info)
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(glesv2)
# Generates the protocol glue for xdg-shell and linux-dmabuf.
BuildRequires:  hyprwayland-scanner-devel >= 0.4.0
# pkgconfig(hwdata) only supplies the pkgdatadir variable. CMake then reads
# pnp.ids out of that directory through data/hwdata.sh at configure time, so the
# data package itself has to be installed too -- with only hwdata-devel present the
# monitor vendor table silently comes out empty ("hwdata gathering pnps failed" is
# a warning, not an error).
BuildRequires:  pkgconfig(hwdata)
BuildRequires:  hwdata

%description
Aquamarine is the backend library Hyprland uses instead of wlroots. It owns
session and device management, the DRM and Wayland backends, buffer allocation
through GBM, and input via libinput.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Headers and pkgconfig file needed to build compositors against %{name}.

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
%{_libdir}/libaquamarine.so.12
%{_libdir}/libaquamarine.so.%{version}

%files devel
%{_includedir}/aquamarine/
%{_libdir}/libaquamarine.so
%{_libdir}/pkgconfig/aquamarine.pc

%changelog
* Wed Aug 05 2026 Saeverix - 0.13.0-1
- Initial package, built for Hyprland
