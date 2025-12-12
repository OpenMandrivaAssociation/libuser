%define major 1
%define libname %mklibname user %{major}
%define devname %mklibname user -d
%global __provides_exclude_from ^(%{_libdir}/%{name}|%{python_sitearch})/.*$
%define enable_check 0

Summary:	A user and group account administration library
Name:		libuser
Version:	0.64
Release:	2
License:	LGPLv2+
Group:		System/Configuration/Other
Url:		https://pagure.io/libuser/
Source0:	https://releases.pagure.org/libuser/libuser-%{version}.tar.gz
BuildRequires:	bison
BuildRequires:	linuxdoc-tools
BuildRequires:	gettext-devel
BuildRequires:	openldap-devel
BuildRequires:	pam-devel
BuildRequires:	gtk-doc
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(popt)
BuildRequires:	pkgconfig(python)
BuildRequires:	pkgconfig(libsasl2)
# https://bugzilla.redhat.com/show_bug.cgi?id=1489451
BuildConflicts: docbook-dtd42-sgml docbook-dtd41-sgml docbook-dtd31-sgml
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

%package python
Group:		Development/Python
Summary:	Library bindings for python

%description python
This package contains the python library for python applications that
use libuser.

%package ldap
Group:		System/Libraries
Summary:	Libuser ldap library

%description ldap
This package contains the libuser ldap library.

%package -n %{libname}
Group:		System/Libraries
Summary:	The actual libraries for libuser

%description -n %{libname}
This is the actual library for the libuser library.

%package -n %{devname}
Group:		Development/C
Summary:	Files needed for developing applications which use libuser
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%description -n %{devname}
This package includes the development files for %{name}.

%prep
%autosetup -p1

# fix tha tests
sed -i -e "s|/etc/openldap/schema|/usr/share/openldap/schema|g" tests/slapd.conf.in

%build
export PYTHON=%{__python}
export CFLAGS="%{optflags} -fPIC -DG_DISABLE_ASSERT -I/usr/include/sasl -DLDAP_DEPRECATED"
./autogen.sh

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
rm -rf %{buildroot}%{py_platsitedir}/*a \
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
%dir %{_libdir}/%{name}/
%{_libdir}/%{name}/libuser_files.so
%{_libdir}/%{name}/libuser_shadow.so
%doc %{_mandir}/man5/*
%doc %{_mandir}/man1/*

%files -n %{libname}
%{_libdir}/libuser.so.%{major}*

%files python
%{py_platsitedir}/*.so

%files ldap
%{_libdir}/%{name}/libuser_ldap.so

%files -n %{devname}
%dir %{_includedir}/libuser
%{_includedir}/libuser/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*
