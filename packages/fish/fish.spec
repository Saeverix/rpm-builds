# fish's own version string does not satisfy the pkgconfig version validation
# Fedora applies to the generated fish.pc. Upstream disables the check in the
# spec template they ship in the tarball; do the same.
%define _wrong_version_format_terminate_build 0

Name:           fish
Version:        4.8.1
Release:        2%{?dist}
Summary:        Friendly interactive shell

# This is upstream's own declaration for the fish source tree. The vendored Rust
# crates add Apache-2.0, MIT, Unlicense, WTFPL and Zlib on top (see Fedora's
# fish package for the full breakdown). We do not generate a
# LICENSE.dependencies file, because that needs cargo-rpm-macros, which this
# package deliberately avoids -- see the Source3 comment below.
License:        GPL-2.0-only AND GPL-2.0-or-later AND BSD-2-Clause AND PSF-2.0 AND ISC AND MIT
URL:            https://fishshell.com
Source0:        https://github.com/fish-shell/fish-shell/releases/download/%{version}/%{name}-%{version}.tar.xz
Source1:        https://github.com/fish-shell/fish-shell/releases/download/%{version}/%{name}-%{version}.tar.xz.asc
# Johannes Altmanninger <aclopte@gmail.com>, fish's release signer.
# Primary key D7E7 B7E3 7EF1 2924 3377  FC0A 6343 29A4 CF8E 23E8
Source2:        https://github.com/krobelus.gpg
# The cargo dependencies, vendored. Upstream does not publish this as a release
# asset, so .woodpecker/fish.yaml generates it before rpmbuild runs -- which is
# why this Source has a bare filename and no URL, so spectool skips it.
#
# fish's Cargo.toml pulls four dependencies straight from git (fluent,
# fluent-syntax, fluent-ftl-tools, and fish's forked pcre2). Fedora's own
# package carries a five-patch stack to strip those out so it can build against
# distro crate packages; vendoring handles git dependencies natively and needs
# no patches at all.
Source3:        %{name}-%{version}-vendor.tar.xz

BuildRequires:  cargo
BuildRequires:  rust >= 1.85
BuildRequires:  cmake >= 3.15
BuildRequires:  ninja-build
BuildRequires:  gcc
BuildRequires:  gettext
BuildRequires:  pcre2-devel
BuildRequires:  ncurses-devel
BuildRequires:  xz
BuildRequires:  pkgconf-pkg-config
BuildRequires:  python3-devel
# Builds the man pages. The release tarball ships no prebuilt docs, so without
# this there is no fish(1) at all.
BuildRequires:  /usr/bin/sphinx-build
# For the Source1 signature check in %%prep.
BuildRequires:  gnupg2
# For %%check.
BuildRequires:  python3-pexpect
BuildRequires:  procps-ng
BuildRequires:  glibc-langpack-en

# fish reads terminfo entries at runtime.
Requires:       ncurses-term
# Tab completion generates completions by parsing man pages.
Recommends:     man-db
Recommends:     man-pages
Recommends:     groff-base

%description
fish is a smart and user-friendly command line shell. It offers syntax
highlighting, autosuggestions from history, and tab completions that work out of
the box without configuration. Its language is simple and consistent, but
deliberately not POSIX compatible.

%prep
%{gpgverify} --keyring='%{SOURCE2}' --signature='%{SOURCE1}' --data='%{SOURCE0}'
# -a 3 unpacks the vendor tarball over the source tree after unpacking Source0.
# %%autosetup cannot do this, so it has to be plain %%setup.
%setup -q -a 3

# Point the bundled helper scripts at the interpreter we actually built against
# rather than whatever `env python3` finds first.
for f in $(find share/tools -type f -name '*.py'); do
    sed -i -e '1{s@^#!.*@#!%{__python3}@}' "$f"
done

%build
# The vendor tarball supplies every crate, so nothing should reach the network.
# If this build ever starts failing with cargo trying to fetch, the vendor step
# in .woodpecker/fish.yaml is what broke, not this spec.
export CARGO_NET_OFFLINE=true
# The CMake macros pass a sysconfdir under the prefix, which puts fish's config
# in /usr/etc. The docdir override keeps upstream's docs out of a versioned
# directory that %%files would then have to guess at.
%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DWITH_DOCS=ON \
    -DCMAKE_INSTALL_SYSCONFDIR=%{_sysconfdir} \
    -DCMAKE_INSTALL_DOCDIR=%{_pkgdocdir} \
    -Dextra_completionsdir=%{_datadir}/%{name}/vendor_completions.d \
    -Dextra_functionsdir=%{_datadir}/%{name}/vendor_functions.d \
    -Dextra_confdir=%{_datadir}/%{name}/vendor_conf.d
%cmake_build

%install
%cmake_install
%py_byte_compile %{python3} %{buildroot}%{_datadir}/%{name}/tools/
cp -a README.rst CONTRIBUTING.rst %{buildroot}%{_pkgdocdir}
# Sphinx's incremental-build metadata. Useless once installed, and rpmlint
# rightly flags it as a stray hidden file.
rm -f %{buildroot}%{_pkgdocdir}/.buildinfo

%check
# CI=1 makes fish skip the tests that need a real terminal, which is what
# Fedora does too. Without it the suite is unreliable in a container.
export CI=1
%cmake_build --target fish_run_tests

%post
if [ "$1" = 1 ]; then
    if [ ! -f %{_sysconfdir}/shells ]; then
        echo "%{_bindir}/fish" > %{_sysconfdir}/shells
        echo "/bin/fish" >> %{_sysconfdir}/shells
    else
        grep -q "^%{_bindir}/fish$" %{_sysconfdir}/shells || echo "%{_bindir}/fish" >> %{_sysconfdir}/shells
        grep -q "^/bin/fish$" %{_sysconfdir}/shells || echo "/bin/fish" >> %{_sysconfdir}/shells
    fi
fi

%postun
if [ "$1" = 0 ] && [ -f %{_sysconfdir}/shells ]; then
    sed -i '\!^%{_bindir}/fish$!d' %{_sysconfdir}/shells
    sed -i '\!^/bin/fish$!d' %{_sysconfdir}/shells
fi

%files
%license COPYING
%{_bindir}/fish*
%{_mandir}/man1/fish*.1*
%dir %{_sysconfdir}/fish
%config(noreplace) %{_sysconfdir}/fish/config.fish
%{_datadir}/fish/
%{_datadir}/pkgconfig/fish.pc
%{_pkgdocdir}

%changelog
* Sun Aug 02 2026 Saeverix - 4.8.1-1
- Initial package
