%global _hardened_build 1

%define beanstalkd_user      beanstalkd
%define beanstalkd_group     %{beanstalkd_user}
%define beanstalkd_home      %{_localstatedir}/lib/beanstalkd
%define beanstalkd_binlogdir %{beanstalkd_home}/binlog

Name:           beanstalkd
Version:        1.13
Release:        1%{?dist}
Summary:        A simple, fast work-queue service

License:        MIT
URL:            http://kr.github.io/%{name}/
Source0:        https://github.com/kr/%{name}/archive/v%{version}.tar.gz
Source1:        %{name}.service
Source2:        %{name}.sysconfig

#Patch1:         beanstalkd-1.10-warnings.patch
#Patch2:         beanstalkd-1.10-mkdtemp.patch

BuildRequires:  systemd gcc gcc-c++
BuildRequires: make

Requires(pre):    shadow-utils
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd

%description
beanstalkd is a simple, fast work-queue service. Its interface is generic,
but was originally designed for reducing the latency of page views in
high-volume web applications by running most time-consuming tasks
asynchronously.


%prep
%autosetup -p1


%build
make LDFLAGS="%{?__global_ldflags}" CFLAGS="%{optflags}" %{?_smp_mflags}


%check
make check


%install
make install PREFIX=%{buildroot}%{_prefix}
%{__install} -p -D -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/%{name}
%{__install} -d -m 0755 %{buildroot}%{beanstalkd_home}
%{__install} -d -m 0755 %{buildroot}%{beanstalkd_binlogdir}
%{__install} -d -m 00755 %{buildroot}%{_mandir}/man1
%{__install} -p -m 0644 doc/%{name}.1 %{buildroot}%{_mandir}/man1/


%pre
getent group %{beanstalkd_group} >/dev/null || groupadd -r %{beanstalkd_group}
getent passwd %{beanstalkd_user} >/dev/null || \
    useradd -r -g %{beanstalkd_user} -d %{beanstalkd_home} -s /sbin/nologin \
    -c "beanstalkd user" %{beanstalkd_user}
exit 0


%post
# make the binlog dir after installation, this is so SELinux does not complain
# about the init script creating the binlog directory
# See RhBug 558310
if [ -d %{beanstalkd_home} ]; then
    %{__install} -d %{beanstalkd_binlogdir} -m 0755 \
        -o %{beanstalkd_user} -g %{beanstalkd_user} \
        %{beanstalkd_binlogdir}
fi
%systemd_post %{name}.service


%preun
%systemd_preun %{name}.service


%postun
%systemd_postun_with_restart %{name}.service


%files
%doc doc/protocol.txt
%license LICENSE
%{_unitdir}/%{name}.service
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1*
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%attr(0755,%{beanstalkd_user},%{beanstalkd_group}) %dir %{beanstalkd_home}
%ghost %attr(0755,%{beanstalkd_user},%{beanstalkd_group}) %dir %{beanstalkd_binlogdir}
