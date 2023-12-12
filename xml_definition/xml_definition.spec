
Name:		xml_definition
Version:	2.3
Release:	2.g%{?rev}
Summary:	XML definition files and configure examples
Group:		Applications/DDN
License:	Share
Packager:	Li Xi <pkuelelixi@gmail.com>
Vendor:		LustrePerfMon
URL:		https://github.com/DDNStorage/LustrePerfMon
Source0:	xml_definition.tar.gz
BuildArch:	noarch
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
%{__install} -Dp -m0644 lustre-ieel-2.7.xml %{buildroot}%{_sysconfdir}/lustre-ieel-2.7_definition.xml
%{__install} -Dp -m0644 lustre-es4-2.10.xml %{buildroot}%{_sysconfdir}/lustre-es4-2.10.xml
%{__install} -Dp -m0644 lustre-2.12.xml %{buildroot}%{_sysconfdir}/lustre-2.12.xml
%{__install} -Dp -m0644 lustre-b_es5_1.xml %{buildroot}%{_sysconfdir}/lustre-b_es5_1.xml
%{__install} -Dp -m0644 lustre-b_es5_2.xml %{buildroot}%{_sysconfdir}/lustre-b_es5_2.xml
%{__install} -Dp -m0644 lustre-b_es6_0.xml %{buildroot}%{_sysconfdir}/lustre-b_es6_0.xml
%{__install} -Dp -m0644 lustre-b_es6_3.xml %{buildroot}%{_sysconfdir}/lustre-b_es6_3.xml
%{__install} -Dp -m0644 lustre-2.13.xml %{buildroot}%{_sysconfdir}/lustre-2.13.xml
%{__install} -Dp -m0644 gpfs-3.5.xml %{buildroot}%{_sysconfdir}/gpfs-3.5_definition.xml
%{__install} -Dp -m0644 sfa-3.0.xml %{buildroot}%{_sysconfdir}/sfa-3.0_definition.xml
%{__install} -Dp -m0644 sfa-11.0.xml %{buildroot}%{_sysconfdir}/sfa-11.0_definition.xml
%{__install} -Dp -m0644 sfa-11.6.xml %{buildroot}%{_sysconfdir}/sfa-11.6_definition.xml
%{__install} -Dp -m0644 collectd.conf.all %{buildroot}%{_sysconfdir}/collectd.conf.all
%{__install} -Dp -m0644 ime-1.1.xml %{buildroot}%{_sysconfdir}
%{__install} -Dp -m0644 ime-1.2.xml %{buildroot}%{_sysconfdir}
%{__install} -Dp -m0644 infiniband-0.1.xml %{buildroot}%{_sysconfdir}/infiniband-0.1_definition.xml
%{__install} -Dp -m0755 ime_monitor_bad_node_filter %{buildroot}%{_bindir}/ime_monitor_bad_node_filter

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
%{_sysconfdir}/lustre-ieel-2.7_definition.xml
%{_sysconfdir}/lustre-es4-2.10.xml
%{_sysconfdir}/lustre-2.12.xml
%{_sysconfdir}/lustre-b_es5_1.xml
%{_sysconfdir}/lustre-b_es5_2.xml
%{_sysconfdir}/lustre-b_es6_0.xml
%{_sysconfdir}/lustre-b_es6_3.xml
%{_sysconfdir}/lustre-2.13.xml
%{_sysconfdir}/gpfs-3.5_definition.xml
%{_sysconfdir}/sfa-3.0_definition.xml
%{_sysconfdir}/sfa-11.0_definition.xml
%{_sysconfdir}/sfa-11.6_definition.xml
%{_sysconfdir}/collectd.conf.all
%{_sysconfdir}/ime-1.1.xml
%{_sysconfdir}/ime-1.2.xml
%{_sysconfdir}/infiniband-0.1_definition.xml
%{_bindir}/ime_monitor_bad_node_filter

%changelog
* Mon Feb 27 2017 Wang Shilong <wshilong@ddn.com> 0.1
- Add infiniband definition file.
* Tue Feb 21 2017 Wang Shilong <wshilong@ddn.com> 3.0
- Bump version of sfa XML.
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
