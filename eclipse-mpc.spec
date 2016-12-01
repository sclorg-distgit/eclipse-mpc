%{?scl:%scl_package eclipse-mpc}
%{!?scl:%global pkg_name %{name}}
%{?java_common_find_provides_and_requires}

%global baserelease 1

%global mpc_repo_tag R_1_5_0a
%global uss_repo_tag 28fcf4edfc8e812332fc2c6bd241fab6e0f56094

Name:           %{?scl_prefix}eclipse-mpc
Version:        1.5.0
Release:        3.%{baserelease}%{?dist}
Summary:        Eclipse Marketplace Client

License:        EPL
URL:            http://www.eclipse.org/mpc/
Source0:        http://git.eclipse.org/c/mpc/org.eclipse.epp.mpc.git/snapshot/org.eclipse.epp.mpc-%{mpc_repo_tag}.tar.xz

# This could be broken out into a separate srpm if something else requires it in the future
Source1:        http://git.eclipse.org/c/oomph/uss.git/snapshot/uss-%{uss_repo_tag}.tar.xz

BuildArch: noarch

BuildRequires: %{?scl_prefix}eclipse-pde
BuildRequires: %{?scl_prefix}eclipse-p2-discovery
BuildRequires: %{?scl_prefix}tycho
BuildRequires: %{?scl_prefix}tycho-extras
BuildRequires: %{?scl_prefix_maven}maven-plugin-build-helper
BuildRequires: %{?scl_prefix_maven}maven-enforcer-plugin
BuildRequires: %{?scl_prefix}eclipse-license
BuildRequires: %{?scl_prefix_java_common}httpcomponents-client
Requires: %{?scl_prefix}eclipse-platform
Requires: %{?scl_prefix}eclipse-p2-discovery

%description
The Eclipse Marketplace Client provides access to extension catalogs.

%prep
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%setup -q -n org.eclipse.epp.mpc-%{mpc_repo_tag}

# Add USS plug-ins to the build
tar --strip-components=1 -xf %{SOURCE1} uss-%{uss_repo_tag}/org.eclipse.userstorage{,.ui}
%pom_xpath_inject "pom:modules" "<module>org.eclipse.userstorage</module><module>org.eclipse.userstorage.ui</module>"
%pom_set_parent "org.eclipse.epp.mpc:org.eclipse.epp.mpc-root:%{version}-SNAPSHOT" org.eclipse.userstorage
%pom_set_parent "org.eclipse.epp.mpc:org.eclipse.epp.mpc-root:%{version}-SNAPSHOT" org.eclipse.userstorage.ui
sed -i -e '/httpclient/i\ org.apache.httpcomponents.fluent-hc;bundle-version="[4.0.0,5.0.0)",' org.eclipse.userstorage/META-INF/MANIFEST.MF

# PMD and findbugs is unnecessary to the build
%pom_remove_plugin org.apache.maven.plugins:maven-pmd-plugin org.eclipse.epp.mpc.ui
%pom_remove_plugin org.apache.maven.plugins:maven-pmd-plugin org.eclipse.epp.mpc-parent/bundle
%pom_remove_plugin org.codehaus.mojo:findbugs-maven-plugin org.eclipse.epp.mpc.ui
%pom_remove_plugin org.codehaus.mojo:findbugs-maven-plugin org.eclipse.epp.mpc-parent/bundle

%pom_remove_plugin org.eclipse.tycho:target-platform-configuration org.eclipse.epp.mpc-parent/pom.xml
%pom_xpath_remove "pom:build/pom:pluginManagement/pom:plugins/pom:plugin[pom:artifactId='tycho-packaging-plugin']" org.eclipse.epp.mpc-parent/pom.xml
%pom_disable_module org.eclipse.epp.mpc.site
%pom_disable_module org.eclipse.epp.mpc.tests
%pom_disable_module org.eclipse.epp.mpc.tests.catalog

# Non-strict compiler checking
sed -i -e '/strictCompilerTarget/d' org.eclipse.epp.mpc-parent/pom.xml

%mvn_package "::pom::" __noinstall
%mvn_package "::jar:sources{,-feature}:"
%{?scl:EOF}


%build
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%mvn_build -j -f -- -DforceContextQualifier=v%(date -u +%%Y%%m%%d-%%H00)
%{?scl:EOF}


%install
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%mvn_install
%{?scl:EOF}


%files -f .mfiles

%changelog
* Mon Aug 01 2016 Mat Booth <mat.booth@redhat.com> - 1.5.0-3.1
- Auto SCL-ise package for rh-eclipse46 collection

* Mon Aug 01 2016 Mat Booth <mat.booth@redhat.com> - 1.5.0-3
- Drop usage of PMD plugin

* Mon Jul 11 2016 Mat Booth <mat.booth@redhat.com> - 1.5.0-2
- Add missing BR

* Mon Jul 11 2016 Mat Booth <mat.booth@redhat.com> - 1.5.0-1
- Update to neon release

* Wed Jun 15 2016 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.4.2-2
- Add missing build-requires

* Wed Mar 09 2016 Mat Booth <mat.booth@redhat.com> - 1.4.2-1
- Update to Mars.2 release

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.4.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Oct 05 2015 Mat Booth <mat.booth@redhat.com> - 1.4.1-1
- Update to Mars.1 release

* Mon Sep 14 2015 Roland Grunberg <rgrunber@redhat.com> - 1.4.0-2
- Rebuild as an Eclipse p2 Droplet.

* Thu Jul 2 2015 Alexander Kurtakov <akurtako@redhat.com> 1.4.0-1
- Update to upstream 1.4.0 release.

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Mar 06 2015 Mat Booth <mat.booth@redhat.com> - 1.3.2-1
- Update to Luna SR2 release

* Fri Feb  6 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.1-5
- Rebuild to generate missing OSGi auto-requires

* Tue Jan 20 2015 Mat Booth <mat.booth@redhat.com> - 1.3.1-4
- Make direct hamcrest use explicit in manifest

* Wed Dec 3 2014 Alexander Kurtakov <akurtako@redhat.com> 1.3.1-3
- Build with xmvn.

* Fri Nov 7 2014 Alexander Kurtakov <akurtako@redhat.com> 1.3.1-2
- Prepend v to qualifier to make update center not proposing updates.

* Tue Oct 07 2014 Roland Grunberg <rgrunber@redhat.com> - 1.3.1-1
- Update to upstream 1.3.1 release.

* Mon Oct 06 2014 Roland Grunberg <rgrunber@redhat.com> - 1.3.0-2
- Make org.eclipse.epp.mpc.core a singleton bundle.
- Resolves: rhbz#1149469

* Thu Sep 11 2014 Alexander Kurtakov <akurtako@redhat.com> 1.3.0-1
- Update to upstream 1.3.0 release.

* Thu Sep 4 2014 Alexander Kurtakov <akurtako@redhat.com> 1.2.2-1
- Update to official 1.2.2 release.

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.1-0.2.git519e70b
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Nov 11 2013 Alexander Kurtakov <akurtako@redhat.com> 1.2.1-0.1.git519e70b
- This is gonna be version 1.2.1.

* Tue Oct 1 2013 Krzysztof Daniel <kdaniel@redhat.com> 1.1.2-0.6.git7feb49
- Fix the build (remove jgit timestamp provider).

* Tue Oct 1 2013 Krzysztof Daniel <kdaniel@redhat.com> 1.1.2-0.4.git7feb49
- Update to latest upstream.

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.2-0.4.git00b427
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Jun 20 2013 Krzysztof Daniel <kdaniel@redhat.com> 1.1.2-0.3.git00b427
- Update to latest upstream (likely Kepler, but not tagged yet).

* Tue May 7 2013 Krzysztof Daniel <kdaniel@redhat.com> 1.1.2-0.2.gitb114a5
- Tranistion to tycho build. 

* Mon May 6 2013 Krzysztof Daniel <kdaniel@redhat.com> 1.1.2-0.1.gitb114a5
- Update to latest upstream.

* Thu Feb 14 2013 Krzysztof Daniel <kdaniel@redhat.com> 1.1.1-4
- Fix the build.

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Feb 10 2012 Alexander Kurtakov <akurtako@redhat.com> 1.1.1-1
- Update to upstream 1.1.1 release.

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Jul 13 2011 Alexander Kurtakov <akurtako@redhat.com> 1.1.0-2
- Use upstream sources.
- Adapt to current guidelines.

* Thu Jun 02 2011 Chris Aniszczyk <zx@redhat.com> 1.1.0-1
- Updating to the 1.1.0 release

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Sep 9 2010 Chris Aniszczyk <zx@redhat.com> 1.0.1-1
- Initial packaging