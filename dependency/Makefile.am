SUBDIRS = .

noinst_DATA = rpms

# We want to check the completeness of RPMs every time,
# since it is not uncommon that downloding RPMs is interrupted,
# And yumdownloader can skip complete RPMs.
rpms:
	yumdownloader --resolve --archlist=x86_64 $(DEPENDENCY_PACKAGES)

$(BUILD_DIRS):
	mkdir $@

clean-local:
	-rm -f $(DEPENDENCY_RPMS)
