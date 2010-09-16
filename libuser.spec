%define	major	1
%define libname	%mklibname user %{major}
%define develname %mklibname user -d

Summary:	A user and group account administration library
Name:		libuser
Version:	0.56.18
Release:	%mkrel 1
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
BuildRequires:	gettext
BuildRequires:	glib2-devel
BuildRequires:	openldap-devel
BuildRequires:	linuxdoc-tools
BuildRequires:	pam-devel
BuildRequires:	popt-devel
BuildRequires:	python-devel
#BuildRequires:	libgsasl-devel
BuildRequires:	bison
Conflicts:	libuser1 <= 0.51-6mdk
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

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
Requires:	%{libname} = %{version}-%{release}

%description python
This package contains the python library for python applications that 
use libuser.

%package ldap
Group:		System/Libraries
Summary:	Libuser ldap library
Requires:	%{libname} = %{version}-%{release}

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
Requires:	%{name} = %{version}-%{release}

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
%patch1 -p1
%patch2 -p0

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

%install
rm -fr %{buildroot}
%makeinstall_std

%find_lang %{name}

# Remove unpackaged files
rm -rf  %{buildroot}/usr/share/man/man3/userquota.3 \
        %{buildroot}%{py_platsitedir}/*a \
        %{buildroot}%{_libdir}/%{name}/*.la

%check
LD_LIBRARY_PATH=%{buildroot}%{_libdir}:${LD_LIBRARY_PATH}
export LD_LIBRARY_PATH

# Verify that all python modules load, just in case.
pushd %{buildroot}/%{_libdir}/python%{pyver}/site-packages/
python -c "import libuser"
popd

%clean
rm -rf %{buildroot}

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%files -f %{name}.lang
%defattr(-,root,root)
%doc AUTHORS NEWS README TODO docs/*.txt python/modules.txt
%config(noreplace) %{_sysconfdir}/libuser.conf
%attr(0755,root,root) %{_bindir}/*
%attr(0755,root,root) %{_sbindir}/*
%dir %{_libdir}/%{name}/
%attr(0755,root,root) %{_libdir}/%{name}/libuser_files.so
%attr(0755,root,root) %{_libdir}/%{name}/libuser_shadow.so
%_mandir/man5/*
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
%defattr(-,root,root)
%attr(0755,root,root) %dir %{_includedir}/libuser
%attr(0644,root,root) %{_includedir}/libuser/*
%attr(0644,root,root) %{_libdir}/*.la
%{_libdir}/*.so
%attr(0644,root,root) %{_libdir}/pkgconfig/*
%{_datadir}/gtk-doc/html/*
