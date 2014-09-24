Name:		montools
Version:	1.0.g%{?rev}.ddn1
Release:	1%{?dist}
Summary:	Monitoring tools of DDN
Group:		Applications/DDN
License:	Share
Packager:	Wu Libin <lwu@ddn.com>
Vendor:		DataDirect Netowrks Inc
URL:		http://www.ddn.com/
Source0:	montools.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root
Requires:	python-carbon
Requires:	python-whisper
Requires:	graphite-web
Requires:	httpd
Requires:	mod_wsgi

%define bindir /usr/local/montools/bin
%define confdir /usr/local/montools/conf

%description
Monitoring tools of DDN

%prep
%setup -c

%build

%install
mkdir -p ${RPM_BUILD_ROOT}%{bindir}
install -m 755 ./graphite-setup.py ${RPM_BUILD_ROOT}%{bindir}/graphite-setup
install -m 755 ./grafana-setup.py ${RPM_BUILD_ROOT}%{bindir}/grafana-setup

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf "$RPM_BUILD_ROOT"
rm -rf $RPM_BUILD_DIR/%{name}-%{version}

%post
echo "Use: '/usr/local/montools/bin/graphite-setup install'" \
     "to config the graphite-web"
echo "Use: '/usr/local/montools/bin/grafana-setup install'" \
     "to config the grafana"

%preun

%postun

%files
%defattr(-,root,root,-)
%{bindir}/graphite-setup
%{bindir}/grafana-setup



%changelog
* Tue May 20 2014 Wu Libin <lwu@ddn.com> 1.0-5
- package collectd graphite-web carbon whisper to rpm, use setup.py to install and config

