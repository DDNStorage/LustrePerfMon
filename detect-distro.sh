#!/bin/bash

if which lsb_release >/dev/null 2>&1; then
	name="$(lsb_release -s -i)"
	version="$(lsb_release -s -r)"
	case "$name" in
		"EnterpriseEnterpriseServer")
			name="oel"
			;;
		"RedHatEnterpriseServer" | "ScientificSL" | "CentOS")
			name="rhel"
			;;
		"SUSE LINUX")
			name="sles"
			PATCHLEVEL=$(sed -n -e 's/^PATCHLEVEL = //p' /etc/SuSE-release)
			version="${version}.$PATCHLEVEL"
			;;
		"Fedora")
			name="fc"
			;;
		*)
			fatal 1 "I don't know what distro name $name and version $version is.\nEither update autodetect_distro() or use the --distro argument."
			;;
		esac
	else
		error "You really ought to install lsb_release for accurate distro identification"
		# try some heuristics
		if [ -f /etc/SuSE-release ]; then
			name=sles
			version=$(sed -n -e 's/^VERSION = //p' /etc/SuSE-release)
			PATCHLEVEL=$(sed -n -e 's/^PATCHLEVEL = //p' /etc/SuSE-release)
			version="${version}.$PATCHLEVEL"
		elif [ -f /etc/redhat-release ]; then
			#name=$(head -1 /etc/redhat-release)
			name=rhel
			version=$(echo "$distroname" |
				sed -e 's/^[^0-9.]*//g' | sed -e 's/[ ].*//')
        fi
		if [ -z "$name" -o -z "$version" ]; then
			fatal 1 "I don't know how to determine distro type/version.\nEither update autodetect_distro() or use the --distro argument."
		fi
	fi

	echo ${name}-${version}
	exit 0
