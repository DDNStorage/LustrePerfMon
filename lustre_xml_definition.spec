Name:		lustre_xml_definition	
Version:	1.0.ddn1
Release:	1.el6
Summary:    XML definition files of lustre	
Group:		Applications/DDN
License:	Share
Packager:	Wu Libin <lwu@ddn.com>
Vendor:		Enterprise information Management.Inc
URL:		http://www.ddn.com/
Source0:	lustre_xml_definition.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description
XML definition files of lustre of DDN

%prep
%setup -c

%build

%install
%{__install} -Dp -m0644 lustre-1.8.9.xml %{buildroot}%{_sysconfdir}/lustre-1.8_definition.xml
%{__install} -Dp -m0644 lustre-2.4.2.xml %{buildroot}%{_sysconfdir}/lustre-2.4_definition.xml
%{__install} -Dp -m0644 lustre-2.5.xml %{buildroot}%{_sysconfdir}/lustre-2.5_definition.xml
%{__install} -Dp -m0644 lustre-ieel-2.5.xml %{buildroot}%{_sysconfdir}/lustre-ieel-2.5_definition.xml
%{__install} -Dp -m0644 collectd.conf.all %{buildroot}%{_sysconfdir}/collectd.conf.all

%clean

%post

%preun

%postun

%files
%defattr(-,root,root,-)
%{_sysconfdir}/lustre-1.8_definition.xml
%{_sysconfdir}/lustre-2.4_definition.xml
%{_sysconfdir}/lustre-2.5_definition.xml
%{_sysconfdir}/lustre-ieel-2.5_definition.xml
%{_sysconfdir}/collectd.conf.all

%changelog
* Fri Jul 5 2014 Wu Libin <lwu@ddn.com> 1.0
- Add collectd.conf.all to this package.
* Fri Jun 20 2014 Wu Libin <lwu@ddn.com> 1.0
- First package, just include XML definition files to this package.

