Name:           hyprgraphics
Version:        0.5.1
Release:        1%{?dist}
Summary:        Graphics and image resource library for the Hyprland ecosystem

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprgraphics
Source0:        %{url}/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(hyprutils)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(libwebp)
BuildRequires:  pkgconfig(librsvg-2.0)
BuildRequires:  pkgconfig(libmagic)
BuildRequires:  pkgconfig(glesv2)
# JPEG XL and AVIF are optional: upstream drops the JpegXL.cpp and Avif.cpp
# sources and the matching compile definitions when these are missing, so leaving
# them out would silently ship a build that cannot open those images. Both are in
# Fedora 44, so ask for them.
BuildRequires:  pkgconfig(libjxl)
BuildRequires:  pkgconfig(libjxl_cms)
BuildRequires:  pkgconfig(libjxl_threads)
BuildRequires:  pkgconfig(libheif)

%description
hyprgraphics handles image loading and colour management for the Hyprland
ecosystem: PNG, JPEG, WebP, SVG, JPEG XL and AVIF decoding, cairo surface
helpers and colour space conversion.

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
%{_libdir}/libhyprgraphics.so.4
%{_libdir}/libhyprgraphics.so.%{version}

%files devel
%{_includedir}/hyprgraphics/
%{_libdir}/libhyprgraphics.so
%{_libdir}/pkgconfig/hyprgraphics.pc

%changelog
* Wed Aug 05 2026 Saeverix - 0.5.1-1
- Initial package, built for Hyprland
