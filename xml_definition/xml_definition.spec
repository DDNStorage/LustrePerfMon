Name:		xml_definition
Version:	1.0.g%{?rev}.ddn1
Release:	1%{?dist}
Summary:	XML definition files and configure examples
Group:		Applications/DDN
License:	Share
Packager:	Wu Libin <lwu@ddn.com>
Vendor:		DataDirect Networks
URL:		http://www.ddn.com/
Source0:	xml_definition.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description
This package includes XML definition files and configure examples for monitor system.

%prep
%setup -c

%build

%install
%{__install} -Dp -m0644 lustre-1.8.9.xml %{buildroot}%{_sysconfdir}/lustre-1.8_definition.xml
%{__install} -Dp -m0644 lustre-2.4.2.xml %{buildroot}%{_sysconfdir}/lustre-2.4_definition.xml
%{__install} -Dp -m0644 lustre-2.1.6.xml %{buildroot}%{_sysconfdir}/lustre-2.1_definition.xml
%{__install} -Dp -m0644 lustre-2.5.xml %{buildroot}%{_sysconfdir}/lustre-2.5_definition.xml
%{__install} -Dp -m0644 lustre-ieel-2.5.xml %{buildroot}%{_sysconfdir}/lustre-ieel-2.5_definition.xml
%{__install} -Dp -m0644 gpfs-3.5.xml %{buildroot}%{_sysconfdir}/gpfs-3.5_definition.xml
%{__install} -Dp -m0644 sfa-0.1.xml %{buildroot}%{_sysconfdir}/sfa-0.1_definition.xml
%{__install} -Dp -m0644 collectd.conf.all %{buildroot}%{_sysconfdir}/collectd.conf.all

%clean

%post

%preun

%postun

%files
%defattr(-,root,root,-)
%{_sysconfdir}/lustre-1.8_definition.xml
%{_sysconfdir}/lustre-2.1_definition.xml
%{_sysconfdir}/lustre-2.4_definition.xml
%{_sysconfdir}/lustre-2.5_definition.xml
%{_sysconfdir}/lustre-ieel-2.5_definition.xml
%{_sysconfdir}/gpfs-3.5_definition.xml
%{_sysconfdir}/sfa-0.1_definition.xml
%{_sysconfdir}/collectd.conf.all

%changelog
* Sun Aug 17 2014 Li Xi <lixi@ddn.com> 1.0
- Add version support for building RPMs
* Wed Aug 13 2014 Li Xi <lixi@ddn.com> 1.0
- Add XML definition file for GPFS 3.5
* Sat Jul 26 2014 Wu Libin <lwu@ddn.com> 1.0
- Add XML definition file for lustre 2.1
* Fri Jul 5 2014 Wu Libin <lwu@ddn.com> 1.0
- Add collectd.conf.all to this package.
* Fri Jun 20 2014 Wu Libin <lwu@ddn.com> 1.0
- First package, just include XML definition files to this package.
