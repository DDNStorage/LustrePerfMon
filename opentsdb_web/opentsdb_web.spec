Name:		opentsdb_web
Version:	1.0.g%{?rev}.ddn1
Release:	1%{?dist}
Summary:	Web interface for openTSDB
Group:		Applications/DDN
License:	Share
Packager:	Li Xi <lixi@ddn.com>
Vendor:		DataDirect Networks, Inc.
URL:		http://www.ddn.com/
Source0:	opentsdb_web.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%define webdir /var/www/html/%{name}

%description
Web interface for openTSDB

%prep
%setup -c

%build

%install
%{__install} -Dp -m0644 angular.min.js %{buildroot}%{webdir}/angular.min.js
%{__install} -Dp -m0644 jobid.js %{buildroot}%{webdir}/jobid.js
%{__install} -Dp -m0644 opentsdb.js %{buildroot}%{webdir}/opentsdb.js
%{__install} -Dp -m0644 pie.html %{buildroot}%{webdir}/pie.html
%{__install} -Dp -m0644 bubble.html %{buildroot}%{webdir}/bubble.html
%{__install} -Dp -m0644 index.html %{buildroot}%{webdir}/index.html

%clean

%post

%preun

%postun

%files
%defattr(-,root,root,-)
%{webdir}/angular.min.js
%{webdir}/jobid.js
%{webdir}/opentsdb.js
%{webdir}/pie.html
%{webdir}/bubble.html
%{webdir}/index.html
