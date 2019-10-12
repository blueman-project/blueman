caja_blueman_sendto.py: blueman_sendto.py.in
	$(SED) -e "s|@FILEMANAGER@|Caja|" $< >$@

nemo_blueman_sendto.py: blueman_sendto.py.in
	$(SED) -e "s|@FILEMANAGER@|Nemo|" $< >$@

nautilus_blueman_sendto.py: blueman_sendto.py.in
	$(SED) -e "s|@FILEMANAGER@|Nautilus|" $< >$@

if HAVE_CAJA_PYTHON
cajasendtodir = $(datadir)/caja-python/extensions
cajasendto_DATA = caja_blueman_sendto.py
endif

if HAVE_NEMO_PYTHON
nemosendtodir = $(datadir)/nemo-python/extensions
nemosendto_DATA = nemo_blueman_sendto.py
endif

if HAVE_NAUTILUS_PYTHON
nautilussendtodir = $(datadir)/nautilus-python/extensions
nautilussendto_DATA = nautilus_blueman_sendto.py
endif

CLEANFILES = caja_blueman_sendto.py nemo_blueman_sendto.py nautilus_blueman_sendto.py
EXTRA_DIST = blueman_sendto.py.in
