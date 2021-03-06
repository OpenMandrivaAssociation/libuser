%define major 1
%define libname %mklibname user %{major}
%define devname %mklibname user -d
%global __provides_exclude_from ^(%{_libdir}/%{name}|%{python2_sitearch}|%{python_sitearch})/.*$
%define enable_check 0

Summary:	A user and group account administration library
Name:		libuser
Version:	0.62
Release:	10
License:	LGPLv2+
Group:		System/Configuration/Other
Url:		https://pagure.io/libuser/
Source0:	https://releases.pagure.org/libuser/libuser-%{version}.tar.xz
# patches merged upstream (to be drop on next update):
Patch0:		libuser-0.56.9-fix-str-fmt.patch
Patch3:		libuser-0.57.1-borkfix.diff
Patch4:		libuser-0.57.7-link-python-module-against-python.patch
BuildRequires:	bison
BuildRequires:	linuxdoc-tools
# To make sure the configure script can find it
BuildRequires:	nscd
BuildRequires:	gettext-devel
BuildRequires:	openldap-devel
BuildRequires:	pam-devel
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(popt)
BuildRequires:	pkgconfig(python3)
BuildRequires:	pkgconfig(libsasl2)
#BuildRequires:	pkgconfig(libgsasl)
%if %{enable_check}
# For %%check
BuildRequires:	openldap-clients
BuildRequires:	openldap-servers
BuildRequires:	openssl
BuildRequires:	fakeroot
%endif
# (tpg) conflict with shadow with blowfish hasing algorithm
Conflicts:	shadow < 4.2.1-24

%description
The libuser library implements a standardized interface for manipulating
and administering user and group accounts.  The library uses pluggable
back-ends to interface to its data sources.

Sample applications modeled after those included with the shadow password
suite are included.

%package	python
Group:		Development/Python
Summary:	Library bindings for python

%description	python
This package contains the python library for python applications that
use libuser.

%package	ldap
Group:		System/Libraries
Summary:	Libuser ldap library

%description	ldap
This package contains the libuser ldap library.

#%package	sasl
#Group:		System/Libraries
#Summary:	Libuser sasl library
#Requires:	%{libname} = %{version}-%{release}

#%description	sasl
#This package contains the libuser sasl library.

%package -n	%{libname}
Group:		System/Libraries
Summary:	The actual libraries for libuser

%description -n	%{libname}
This is the actual library for the libuser library.

%package -n	%{devname}
Group:		Development/C
Summary:	Files needed for developing applications which use libuser
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%description -n	%{devname}
This package includes the development files for %{name}.

%prep
%setup -q
%patch0 -p0
%patch3 -p0
#patch4 -p1 -b .python~

# fix tha tests
perl -pi -e "s|/etc/openldap/schema|/usr/share/openldap/schema|g" tests/slapd.conf.in

autoreconf -fi

%build
export PYTHON=%{__python}
export CFLAGS="%{optflags} -fPIC -DG_DISABLE_ASSERT -I/usr/include/sasl -DLDAP_DEPRECATED"

%configure \
	--with-ldap \
	--with-python \
	--with-popt \
	--without-sasl \
	--without-selinux \
	--enable-gtk-doc=no

%make_build

%if %{enable_check}
%check
# note: the tests uses fixed ports 3890 and 6360
LD_LIBRARY_PATH=%{buildroot}%{_libdir}:${LD_LIBRARY_PATH}
export LD_LIBRARY_PATH

# Verify that all python modules load, just in case.
cd %{buildroot}/%{_libdir}/python%{py_ver}/site-packages/
LC_ALL=en_US.UTF-8 %{__python} -c "import libuser"
cd -

# check it
%ifnarch %{ix86} %{x86_64}
LC_ALL=en_US.UTF-8 make check || { cat test-suite.log; false; }
%endif
%endif

%install
%make_install

%find_lang %{name}

# Remove unpackaged files
rm -rf %{buildroot}/usr/share/man/man3/userquota.3 \
	%{buildroot}%{py_platsitedir}/*a \
	%{buildroot}%{_libdir}/%{name}/*.la \
	%{buildroot}%{_libdir}/*.la

# kill /etc/shadow.lock due to algo change
%triggerin -- %{name} < %{EVRD}
for i in gshadow shadow passwd group; do
	rm -f /etc/$i.lock ||: ;
done

%files -f %{name}.lang
%doc AUTHORS NEWS README TODO docs/*.txt python/modules.txt
%config(noreplace) %{_sysconfdir}/libuser.conf
%{_bindir}/*
%{_sbindir}/*
%dir %{_libdir}/%{name}/
%{_libdir}/%{name}/libuser_files.so
%{_libdir}/%{name}/libuser_shadow.so
%{_mandir}/man5/*
%{_mandir}/man1/*

%files -n %{libname}
%{_libdir}/libuser.so.%{major}*

%files python
%{py_platsitedir}/*.so

%files ldap
%{_libdir}/%{name}/libuser_ldap.so

#%files sasl
#%attr(0755,root,root) %{_libdir}/%{name}/libuser_sasldb.so

%files -n %{devname}
%dir %{_includedir}/libuser
%{_includedir}/libuser/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*
%{_datadir}/gtk-doc/html/*
