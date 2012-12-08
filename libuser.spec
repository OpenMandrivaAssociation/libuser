%define	major	1
%define libname	%mklibname user %{major}
%define develname %mklibname user -d

%define enable_check 0

Summary:	A user and group account administration library
Name:		libuser
Version:	0.57.6
Release:	1
License:	LGPLv2+
Group:		System/Configuration/Other
URL:		https://fedorahosted.org/libuser/
Source0:	https://fedorahosted.org/releases/l/i/libuser/%{name}-%{version}.tar.xz
# patches merged upstream (to be drop on next update):
Patch0:		libuser-0.56.9-fix-str-fmt.patch
# default to blowfish for passwords instead of md5 (#59158)
Patch1:		libuser-0.56.15-blowfish.patch
# crypt returns *0 if key is small than 22 and rounds are not given
Patch2:		libuser-0.56.15-fix_blowfish.patch
Patch3:		libuser-0.57.1-borkfix.diff
BuildRequires:	gettext
BuildRequires:	glib2-devel
BuildRequires:	openldap-devel
BuildRequires:	linuxdoc-tools
BuildRequires:	pam-devel
BuildRequires:	popt-devel
BuildRequires:	python-devel
#BuildRequires:	libgsasl-devel
BuildRequires:	bison
%if %{enable_check}
# For %%check
BuildRequires:	openldap-servers openldap-clients
%endif
# To make sure the configure script can find it
BuildRequires:	nscd
Conflicts:	libuser1 <= 0.51-6mdk

%description
The libuser library implements a standardized interface for manipulating
and administering user and group accounts.  The library uses pluggable
back-ends to interface to its data sources.

Sample applications modeled after those included with the shadow password
suite are included.

%package python
Group:		Development/Python
Summary:	Library bindings for python
%py_requires -d

%description python
This package contains the python library for python applications that 
use libuser.

%package ldap
Group:		System/Libraries
Summary:	Libuser ldap library

%description ldap
This package contains the libuser ldap library.

#%package sasl
#Group:		System/Libraries
#Summary:	Libuser sasl library
#Requires:	%{libname} = %{version}-%{release}

#%description sasl
#This package contains the libuser sasl library.

%package -n %{libname}
Group:		System/Libraries
Summary:	The actual libraries for libuser

%description -n	%{libname}
This is the actual library for the libuser library.

%package -n %{develname}
Group:		Development/C
Summary:	Files needed for developing applications which use libuser
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%mklibname -d user 1

%description -n	%{develname}
The libuser-devel package contains header files, static libraries, and other
files useful for developing applications with libuser.

%prep
%setup -q
%patch0 -p0
%patch1 -p0
%patch2 -p0
%patch3 -p0

# fix tha tests
perl -pi -e "s|/etc/openldap/schema|/usr/share/openldap/schema|g" tests/slapd.conf.in

%build
export CFLAGS="%{optflags} -fPIC -DG_DISABLE_ASSERT -I/usr/include/sasl -DLDAP_DEPRECATED"
%configure2_5x \
	--with-ldap \
	--with-python \
	--with-popt \
	--without-sasl \
	--disable-rpath \
	--without-selinux \
	--enable-gtk-doc=no
%make

%if %{enable_check}
%check
# note: the tests uses fixed ports 3890 and 6360
#LD_LIBRARY_PATH=%{buildroot}%{_libdir}:${LD_LIBRARY_PATH}
#export LD_LIBRARY_PATH
make check
%endif

%install
rm -fr %{buildroot}
%makeinstall_std

%find_lang %{name}

# Remove unpackaged files
rm -rf  %{buildroot}/usr/share/man/man3/userquota.3 \
        %{buildroot}%{py_platsitedir}/*a \
        %{buildroot}%{_libdir}/%{name}/*.la \
        %{buildroot}%{_libdir}/*.la

LD_LIBRARY_PATH=%{buildroot}%{_libdir}:${LD_LIBRARY_PATH}
export LD_LIBRARY_PATH

# Verify that all python modules load, just in case.
pushd %{buildroot}/%{_libdir}/python%{py_ver}/site-packages/
    python -c "import libuser"
popd

%files -f %{name}.lang
%doc AUTHORS NEWS README TODO docs/*.txt python/modules.txt
%config(noreplace) %{_sysconfdir}/libuser.conf
%attr(0755,root,root) %{_bindir}/*
%attr(0755,root,root) %{_sbindir}/*
%dir %{_libdir}/%{name}/
%attr(0755,root,root) %{_libdir}/%{name}/libuser_files.so
%attr(0755,root,root) %{_libdir}/%{name}/libuser_shadow.so
%{_mandir}/man5/*
%{_mandir}/man1/*

%files -n %{libname}
%attr(0755,root,root) %{_libdir}/libuser.so.%{major}*

%files python
%attr(0755,root,root) %{py_platsitedir}/*.so

%files ldap
%attr(0755,root,root) %{_libdir}/%{name}/libuser_ldap.so

#%files sasl
#%attr(0755,root,root) %{_libdir}/%{name}/libuser_sasldb.so

%files -n %{develname}
%attr(0755,root,root) %dir %{_includedir}/libuser
%attr(0644,root,root) %{_includedir}/libuser/*
%{_libdir}/*.so
%attr(0644,root,root) %{_libdir}/pkgconfig/*
%{_datadir}/gtk-doc/html/*


%changelog
* Mon May 02 2011 Oden Eriksson <oeriksson@mandriva.com> 0.57.1-2mdv2011.0
+ Revision: 661536
- mass rebuild

* Wed Jan 26 2011 Oden Eriksson <oeriksson@mandriva.com> 0.57.1-1
+ Revision: 632934
- fix the tests again...
- attempt to fix the test suite some more
- 0.57.1
- added P10 from fedora
- rediffed P2 (libuser-0.56.15-blowfish.patch)
- make the test suite work

* Thu Nov 04 2010 Götz Waschk <waschk@mandriva.org> 0.56.18-3mdv2011.0
+ Revision: 593320
- rebuild for new python 2.7

* Thu Sep 16 2010 Tomasz Pawel Gajc <tpg@mandriva.org> 0.56.18-1mdv2011.0
+ Revision: 579049
- update to new version 0.56.18

* Sun Aug 29 2010 Tomasz Pawel Gajc <tpg@mandriva.org> 0.56.17-1mdv2011.0
+ Revision: 574111
- update to new version 0.56.17

* Sat Aug 07 2010 Funda Wang <fwang@mandriva.org> 0.56.16-2mdv2011.0
+ Revision: 567458
- rebuild

  + Tomasz Pawel Gajc <tpg@mandriva.org>
    - update to new version 0.56.16

* Thu May 20 2010 Pascal Terjan <pterjan@mandriva.org> 0.56.15-3mdv2010.1
+ Revision: 545479
- fix blowfish encoding

* Tue May 18 2010 Pascal Terjan <pterjan@mandriva.org> 0.56.15-2mdv2010.1
+ Revision: 545158
- default to blowfish for passwords instead of md5 (#59158)

* Sat Mar 20 2010 Emmanuel Andry <eandry@mandriva.org> 0.56.15-1mdv2010.1
+ Revision: 525491
- New version 0.56.15

* Sat Feb 13 2010 Tomasz Pawel Gajc <tpg@mandriva.org> 0.56.14-1mdv2010.1
+ Revision: 505549
- update to new version 0.56.14
- drop patches 1 and 2, fixed upstream

  + Thierry Vignaud <tv@mandriva.org>
    - add patches status

* Tue Feb 02 2010 Thierry Vignaud <tv@mandriva.org> 0.56.13-2mdv2010.1
+ Revision: 499466
- fix build on x86_64
- patch 1: fix translating in library callers (eg: userdrake)
- patch 2: update french translation

* Thu Dec 31 2009 Tomasz Pawel Gajc <tpg@mandriva.org> 0.56.13-1mdv2010.1
+ Revision: 484480
- update to new version 0.56.13

* Sat Nov 07 2009 Tomasz Pawel Gajc <tpg@mandriva.org> 0.56.12-1mdv2010.1
+ Revision: 462242
- update to new version 0.56.12

* Wed Sep 23 2009 Emmanuel Andry <eandry@mandriva.org> 0.56.11-1mdv2010.0
+ Revision: 447892
- New version 0.56.11

* Sun Jun 28 2009 Tomasz Pawel Gajc <tpg@mandriva.org> 0.56.10-1mdv2010.0
+ Revision: 390224
- disable sasl support
- update to new version 0.56.10
- enable sasl support
- disable rpath
- do not package COPYING file
- spec file clean

* Sat Dec 27 2008 Funda Wang <fwang@mandriva.org> 0.56.9-3mdv2009.1
+ Revision: 319796
- fix str fmt
- rebuild for new python

* Wed Aug 06 2008 Thierry Vignaud <tv@mandriva.org> 0.56.9-2mdv2009.0
+ Revision: 264935
- rebuild early 2009.0 package (before pixel changes)

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Sun Jun 01 2008 Funda Wang <fwang@mandriva.org> 0.56.9-1mdv2009.0
+ Revision: 213923
- New version 0.56.9

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

* Wed Dec 26 2007 Oden Eriksson <oeriksson@mandriva.com> 0.56.4-2mdv2008.1
+ Revision: 137968
- rebuilt against openldap-2.4.7 libs

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Fri Aug 17 2007 Thierry Vignaud <tv@mandriva.org> 0.56.4-1mdv2008.0
+ Revision: 64895
- new release


* Tue Jan 30 2007 Götz Waschk <waschk@mandriva.org> 0.54.5-2mdv2007.0
+ Revision: 115557
- fix devel package conflicting with the main one

* Tue Jan 30 2007 Götz Waschk <waschk@mandriva.org> 0.54.5-1mdv2007.1
+ Revision: 115454
- Import libuser

* Tue Jan 30 2007 Götz Waschk <waschk@mandriva.org> 0.54.5-1mdv2007.1
- rebuild

* Thu Apr 13 2006 Thierry Vignaud <tvignaud@mandriva.com> 0.54.5-1mdk
- new release (fix #21962)
- use %%mkrel

* Wed Sep 07 2005 Oden Eriksson <oeriksson@mandriva.com> 0.53.2-6mdk
- pass "-DLDAP_DEPRECATED" to the CFLAGS

* Wed Aug 31 2005 Buchan Milne <bgmilne@linux-mandrake.com> 0.53.2-5mdk
- Rebuild for new libldap-2.3
- buildrequire openldap-devel, not libldap-devel

* Thu Aug 25 2005 Daouda LO <daouda@mandrakesoft.com> 0.53.2-4mdk
- split out libldap into a new package

* Mon Feb 14 2005 Gwenole Beauchesne <gbeauchesne@mandrakesoft.com> 0.53.2-3mdk
- mklibname

* Fri Feb 04 2005 Buchan Milne <bgmilne@linux-mandrake.com> 0.53.2-2mdk
- rebuild for ldap2.2_7

* Thu Jan 20 2005 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 0.53.2-1mdk
- 0.53.2

* Mon Jan 03 2005 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 0.53.1-1mdk
- 0.53.1
- cosmetics

* Tue Dec 07 2004 Gåtz Waschk <waschk@linux-mandrake.com> 0.53-1mdk
- add new files
- drop all patches
- remove useless files from the devel package
- use pyver macro
- new version

* Tue May 18 2004 Nicolas Planel <nplanel@mandrakesoft.com> 0.51.7-10mdk
- security fix (MDKSA-2004:044).

* Wed Mar 24 2004 Daouda LO <daouda@mandrakesoft.com> 0.51.7-9mdk
- Obsoletes libuser < 0.51-6mdk (9.1 version)

