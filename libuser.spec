%define	major	1
%define libname	%mklibname user %{major}

Summary:	A user and group account administration library
Name:		libuser
Version:	0.56.4
Release:	%mkrel 1
License:	LGPL
Group:		System/Configuration/Other
URL:		http://qa.mandriva.com/
Source0:	libuser-%{version}.tar.bz2
BuildRequires:	gettext	glib2-devel openldap-devel linuxdoc-tools pam-devel popt-devel python-devel
Conflicts:	libuser1 <= 0.51-6mdk

%description
The libuser library implements a standardized interface for manipulating
and administering user and group accounts.  The library uses pluggable
back-ends to interface to its data sources.

Sample applications modeled after those included with the shadow password
suite are included.

%package -n	%{name}-python
Group:		Development/Python
Summary:	Library bindings for python

%description -n	%{name}-python
this package contains the python library for python applications that 
use libuser

%package -n	%{name}-ldap
Group:		System/Libraries
Summary:	Libuser ldap library 

%description -n	%{name}-ldap
this package contains the libuser ldap library

%package -n	%{libname}
Group:		System/Libraries
Summary:	The actual libraries for libuser

%description -n	%{libname}
This is the actual library for the libuser library.

%package -n	%{libname}-devel
Group:		Development/C
Summary:	Files needed for developing applications which use libuser
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%description -n	%{libname}-devel
The libuser-devel package contains header files, static libraries, and other
files useful for developing applications with libuser.

%prep
%setup -q
%build
export CFLAGS="$RPM_OPT_FLAGS -DG_DISABLE_ASSERT -I/usr/include/sasl -DLDAP_DEPRECATED"
%configure2_5x \
	--with-ldap \
	--with-python-version=%{pyver} \
	--with-python-path=%{_includedir}/python%{pyver} \
	--enable-gtk-doc=no
%make 

%install
rm -fr $RPM_BUILD_ROOT
%makeinstall_std

LD_LIBRARY_PATH=$RPM_BUILD_ROOT%{_libdir}:${LD_LIBRARY_PATH}
export LD_LIBRARY_PATH

# Verify that all python modules load, just in case.
pushd $RPM_BUILD_ROOT/%{_libdir}/python%{pyver}/site-packages/
python -c "import libuser"
popd

# RH cruft.
# too disgusting to watch.
set -x
pushd po
rm -rf $RPM_BUILD_ROOT%_datadir/locale
for i in *.po; do
    msgfmt $i -o $(basename $i .po).mo
    p=$RPM_BUILD_ROOT%_datadir/locale/$(basename $i .po)/LC_MESSAGES
    mkdir -p $p
    install -m644 $(basename $i .po).mo $p/libuser.mo
done
popd
rm -rf $RPM_BUILD_ROOT%_datadir/locale/zh_TW.Big5
set +x
%find_lang %{name}

# Remove unpackaged files
rm -rf	$RPM_BUILD_ROOT/usr/share/man/man3/userquota.3 \
	%buildroot%{py_platsitedir}/*a \
	%buildroot%_libdir/%name/*.la

%clean
rm -rf $RPM_BUILD_ROOT

%post -n %{libname} -p /sbin/ldconfig

%postun -n %{libname} -p /sbin/ldconfig

%files -f %{name}.lang
%defattr(-,root,root)
%doc AUTHORS COPYING NEWS README TODO docs/*.txt python/modules.txt
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

%files -n %{name}-python
%attr(0755,root,root) %{py_platsitedir}/*.so

%files -n %{name}-ldap
%attr(0755,root,root) %{_libdir}/%{name}/libuser_ldap.so

%files -n %{libname}-devel
%defattr(-,root,root)
%attr(0755,root,root) %dir %{_includedir}/libuser
%attr(0644,root,root) %{_includedir}/libuser/*
%attr(0644,root,root) %{_libdir}/*.la
%{_libdir}/*.so
#%attr(0644,root,root) %{_mandir}/man3/*
%attr(0644,root,root) %{_libdir}/pkgconfig/*

%{_datadir}/gtk-doc/html/*


