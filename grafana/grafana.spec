Name:		grafana
Version:	%{?brev}.g%{?rev}.ddn1
Release:	1%{?dist}
Summary:	Dashboard of Graphite	
Group:		Applications/DDN
License:	Share
Packager:	Wu Libin <lwu@ddn.com>
Vendor:		Enterprise information Management.Inc
URL:		http://www.ddn.com/
Source0:	grafana.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root
Requires:	graphite-web
Requires:	elasticsearch
Requires:	java
Requires:	java-openjdk

%define homedir /usr/local/%{name}

%description
Dashboard of graphite

%prep
%setup -c

%build

%install
mkdir -p ${RPM_BUILD_ROOT}%{homedir}
cp -rf * ${RPM_BUILD_ROOT}%{homedir}

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf "$RPM_BUILD_ROOT"
rm -rf $RPM_BUILD_DIR/%{name}-%{version}

%post

%preun

%postun

%files
%defattr(-,root,root,-)
%{homedir}

