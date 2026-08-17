# Header-only: nothing is compiled, so there is no ELF for rpm to extract
# debuginfo from, and without this rpm generates a debugsource package and then
# fails the build with "Empty %%files file ... debugsourcefiles.list".
%global debug_package %{nil}

Name:           glaze
# Do NOT bump this to 8.x. Hyprland's CMakeLists asks for `find_package(glaze
# 7...<8)` and falls back to fetching v7.2.0, so glaze 8 is excluded by upstream's
# own version range -- a "latest release" bump here breaks the Hyprland build rather
# than improving anything. Checked against Hyprland v0.56.2.
Version:        7.2.0
Release:        1%{?dist}
Summary:        Header-only C++ JSON and reflection library

License:        MIT
URL:            https://github.com/stephenberry/glaze
Source0:        %{url}/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz

# CXX is declared by project(), so cmake probes for a compiler even though nothing
# is compiled here.
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build

%description
Glaze is a header-only C++ library for JSON, BEVE and CSV serialisation built on
compile-time reflection. Hyprland uses it for its IPC and configuration
marshalling.

# Header-only, so there is no runtime library and nothing to put in a base package:
# this spec has no main %%files section and builds only glaze-devel.
%package        devel
Summary:        Development files for %{name}
# Every installed file is architecture independent -- headers plus the CMake
# package config, which upstream writes with ARCH_INDEPENDENT and installs under
# datadir rather than libdir.
BuildArch:      noarch

%description    devel
Headers and CMake package configuration for %{name}.

%prep
%autosetup

%build
# Hyprland's CMakeLists falls back to FetchContent for glaze when find_package
# comes up empty, which would reach for github mid-build. This package exists to
# make that fallback unreachable, so the version has to stay inside Hyprland's
# declared 7...<8 range -- upstream's own fallback pins v7.2.0. Do not bump this to
# 8.x with Hyprland 0.56.
#
# glaze_DEVELOPER_MODE is a cmake_dependent_option that defaults to ON whenever
# glaze is the top-level project, which a distro build always is. Left on, it adds
# the test suite, the examples, an IDE target and the fuzzers -- and the fuzzers
# link with -fsanitize=address, which fails outright here because libasan is not
# installed. With it off nothing is compiled at all, which is what a header-only
# package should be doing.
#
# glaze_INSTALL also defaults to on for a top-level build, but say it explicitly:
# the whole point of the package is the install rules.
%cmake -GNinja \
    -Dglaze_DEVELOPER_MODE=OFF \
    -Dglaze_INSTALL=ON \
    -Dglaze_BUILD_EXAMPLES=OFF \
    -DBUILD_TESTING=OFF
%cmake_build

%install
%cmake_install

%files devel
%license LICENSE
%doc README.md
%{_includedir}/glaze/
%{_datadir}/glaze/

%changelog
* Wed Aug 05 2026 Saeverix - 7.2.0-1
- Initial package, built for Hyprland
