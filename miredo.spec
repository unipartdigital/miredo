# vim: expandtab

%if 0%{?rhel}
%define withjudy 0
%define with_systemd_rpm_macros 0
%else
%define withjudy 1
%define with_systemd_rpm_macros 1
%endif

%global _hardened_build 1

Name:           miredo
Version:        1.2.6
Release:        11%{?dist}
Summary:        Tunneling of IPv6 over UDP through NATs

Group:          Applications/Internet
License:        GPLv2+
URL:            http://www.remlab.net/miredo/
Source0:        http://www.remlab.net/files/miredo/miredo-%{version}.tar.xz
Source1:        miredo-client.service
Source2:        miredo-server.service
Patch0:         miredo-config-not-exec
Patch1:         reread-resolv-before-resolv-ipv4.patch

BuildRequires:  gcc
BuildRequires:    libcap-devel 
BuildRequires:    autoconf
%if %{withjudy}
BuildRequires:     Judy-devel
%endif

%if 0%{?with_systemd_rpm_macros}
BuildRequires:  systemd-rpm-macros
%endif

%description
Miredo is an implementation of the "Teredo: Tunneling IPv6 over UDP
through NATs" proposed Internet standard (RFC4380). It can serve
either as a Teredo client, a stand-alone Teredo relay, or a Teredo
server, please install the miredo-server or miredo-client appropriately.
It is meant to provide IPv6 connectivity to hosts behind NAT
devices, most of which do not support IPv6, and not even
IPv6-over-IPv4 (including 6to4).

%package libs
Summary:        Tunneling of IPv6 over UDP through NATs
Group:          Applications/Internet 
Requires(pre):    shadow-utils


%description libs
Miredo is an implementation of the "Teredo: Tunneling IPv6 over UDP
through NATs" proposed Internet standard (RFC4380). It can serve
either as a Teredo client, a stand-alone Teredo relay, or a Teredo
server, please install the miredo-server or miredo-client appropriately.
It is meant to provide IPv6 connectivity to hosts behind NAT
devices, most of which do not support IPv6, and not even
IPv6-over-IPv4 (including 6to4).
This libs package provides the files necessary for both server and client.


%package devel
Summary:        Header files, libraries and development documentation for %{name}
Group:          Development/Libraries
Requires:       %{name}-libs = %{version}-%{release}

%description devel
This package contains the header files, development libraries and development
documentation for %{name}. If you would like to develop programs using %{name},
you will need to install %{name}-devel.

%package server
Summary:        Tunneling server for IPv6 over UDP through NATs
Group:          Applications/Internet
Requires:       %{name}-libs = %{version}-%{release}
%description server
Miredo is an implementation of the "Teredo: Tunneling IPv6 over UDP
through NATs" proposed Internet standard (RFC4380). This offers the server 
part of miredo. Most people will need only the client part.

%package client
Summary:        Tunneling client for IPv6 over UDP through NATs
Group:          Applications/Internet
Requires:       %{name}-libs = %{version}-%{release}
Provides:       %{name} = %{version}-%{release}
Obsoletes:      %{name} <= 1.1.6


%description client
Miredo is an implementation of the "Teredo: Tunneling IPv6 over UDP
through NATs" proposed Internet standard (RFC4380). This offers the client
part of miredo. Most people only need the client part.

%prep
%setup -q
%patch0 -p1 
%patch1 -p1
autoconf

%build
%configure \
               --disable-static \
               --disable-rpath \
               --enable-miredo-user \
%if %{withjudy} == 0
               --without-Judy \
%endif


# rpath does not really work
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
make %{?_smp_mflags}


%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot} INSTALL='install -p'
%find_lang %{name}
mkdir rpmdocs
mv %{buildroot}%{_docdir}/miredo/examples rpmdocs/
mkdir -p %{buildroot}%{_unitdir}
install -p -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/miredo-client.service
install -p -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/miredo-server.service
rm -f %{buildroot}%{_libdir}/lib*.la
# We use our own service file
rm -f %{buildroot}/usr/lib*/systemd/system/miredo.service
touch %{buildroot}%{_sysconfdir}/miredo/miredo-server.conf


%pre libs
getent group miredo >/dev/null || groupadd -r miredo
getent passwd miredo >/dev/null || useradd -r -g miredo -d /etc/miredo \
         -s /sbin/nologin -c "Miredo Daemon" miredo
exit 0

%post client
%systemd_post %{name}-client.service

%post server
%systemd_post %{name}-server.service

%preun client
%systemd_preun %{name}-client.service

%preun server
%systemd_preun %{name}-server.service

%postun client
%systemd_postun_with_restart %{name}-client.service

%postun server
%systemd_postun_with_restart %{name}-server.service

%files libs -f %{name}.lang
%doc AUTHORS ChangeLog COPYING NEWS README THANKS TODO rpmdocs/*
%{_libdir}/libteredo.so.*
%{_libdir}/libtun6.so.*

%files devel
%{_includedir}/libteredo/
%{_includedir}/libtun6/
%{_libdir}/libteredo.so
%{_libdir}/libtun6.so

%files server
%ghost %config(noreplace,missingok) %{_sysconfdir}/miredo/miredo-server.conf
%{_bindir}/teredo-mire
%{_sbindir}/miredo-server
%{_sbindir}/miredo-checkconf
%{_unitdir}/miredo-server.service
%doc %{_mandir}/man1/teredo-mire*
%doc %{_mandir}/man?/miredo-server*
%doc %{_mandir}/man?/miredo-checkconf*


%files client
%config(noreplace) %{_sysconfdir}/miredo/miredo.conf
%config(noreplace) %{_sysconfdir}/miredo/client-hook
%{_unitdir}/miredo-client.service
%{_sbindir}/miredo
%{_libexecdir}/miredo/miredo-privproc
%doc %{_mandir}/man?/miredo.*


%changelog
* Sun Jun  7 2020 Michael Brown <mbrown@fensystems.co.uk> - 1.2.6-11
- Update for current Fedora and EPEL releases

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.6-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.6-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.6-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.6-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.6-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.6-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.6-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Aug 05 2013 Jens <bugzilla-redhat@jens.kuehnel.org> - 1.2.6-1
- upgrade to 1.2.6
- fix missing buildreq systemd-units

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.5-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Apr 23 2013 Jens <bugzilla-redhat@jens.kuehnel.org> - 1.2.5-4
- Add PIE Compilier Flag

* Mon Mar 25 2013 Jens <bugzilla-redhat@jens.kuehnel.org> - 1.2.5-3
- add autoconf for aarch64 support

* Fri Mar 22 2013 Jens <bugzilla-redhat@jens.kuehnel.org> - 1.2.5-2
- Fix deletion of mirdeo.service file for 32bit

* Thu Mar 21 2013 Jens Kuehnel <bugzilla-redhat@jens.kuehnel.org> - 1.2.5-1
- Update to 1.2.5

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.7-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.7-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Apr 24 2012 Jon Ciesla <limburgher@gmail.com> - 1.1.7-8
- Migrate to systemd, BZ 789782.

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.7-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.7-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Aug 04 2010 "Jens Kuehnel <fedora-package@jens.kuehnel.org>" - 1.1.7-5
- Fixed BZ#606106 - miredo-client fails to notice resolv.conf changes

* Thu Jul 30 2009 Jens Kuehnel <fedora-package@jens.kuehnel.org> - 1.1.7-4
- Fix Obsoletes for smooth upgrade

* Tue Jul 28 2009 Jens Kuehnel <fedora-package@jens.kuehnel.org> - 1.1.7-3
- without July as optional, hopefully the last EL fix

* Sun Jul 19 2009 Jens Kuehnel <fedora-package@jens.kuehnel.org> - 1.1.7-2
- rename miredo to miredo-libs
- fixes EL

* Tue Jul 14 2009 Jens Kuehnel <fedora-package@jens.kuehnel.org> - 1.1.7-1
- split into server and client package
- update to upstream 1.1.7

* Sun Jun 28 2009 Jens Kuehnel <fedora-package@jens.kuehnel.org> - 1.1.6-2
- renamed miredo startscript to miredo-client
- preliminary preperation for EL
- miredo-server.conf ghosted
- removed .la files instead excluding of them
- fixed ldconfig requires

* Sat Jun 27 2009 Jens Kuehnel <fedora-package@jens.kuehnel.org> - 1.1.6-1
- ReInitiate Fedora package review
- update to 1.1.6
- removed isatap stuff
- don't start it by default

* Sun Oct 05 2008 Charles R. Anderson <cra@wpi.edu> - 1.1.5-1
- Initial Fedora package based on Dries miredo.spec 5059
- Updated to 1.1.5
- disable-static libs
- remove hardcoded rpaths
- create initscripts for client, server, and isatap daemon
- create system user miredo for daemon to setid to
