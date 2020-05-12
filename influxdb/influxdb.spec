Name:		influxdb
Version:	1.8.0
Release:	1
Summary:	Distributed time-series database.
License:	Proprietary
Packager:	Li Xi <pkuelelixi@gmail.com>
Vendor:		InfluxData
URL:		https://influxdata.com
Source:		influxdb.tar.gz

%define __debug_install_post \
%{_rpmconfigdir}/find-debuginfo.sh %{?_find_debuginfo_opts} "%{_builddir}/%{?buildsubdir}"\
%{nil}

%description
Distributed time-series database.

%prep
%setup -c

%build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_bindir}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/influxdb
mkdir -p $RPM_BUILD_ROOT%{_libdir}/influxdb/scripts
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1
mkdir -p $RPM_BUILD_ROOT/var/log/influxdb
cp build/influx \
    build/influxd \
    build/influx_inspect \
    build/influx_stress \
    build/influx_tsm \
	$RPM_BUILD_ROOT%{_bindir}
cp influxdb.conf $RPM_BUILD_ROOT%{_sysconfdir}/influxdb
install -m 0644 -D scripts/influxdb.service \
    $RPM_BUILD_ROOT%{_unitdir}/influxdb.service
cp scripts/logrotate $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/influxdb
cp man/* $RPM_BUILD_ROOT%{_mandir}/man1/

%clean

%post

%preun

%postun

%files
%{_bindir}/influx
%{_bindir}/influxd
%{_bindir}/influx_inspect
%{_bindir}/influx_stress
%{_bindir}/influx_tsm
%config(noreplace) %{_sysconfdir}/influxdb/influxdb.conf
%{_unitdir}/influxdb.service
%{_sysconfdir}/logrotate.d/influxdb
%{_mandir}/man1/*
/var/log/influxdb

%changelog
* Tue May 12 2020 Li Xi <lixi@ddn.com> 1.0
- Create this spec file
