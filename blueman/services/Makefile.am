SUBDIRS = meta

bluemandir = $(pythondir)/blueman/services
blueman_PYTHON =     		\
	__init__.py 	   		\
	DialupNetwork.py    	\
	Functions.py		\
	GroupNetwork.py		    \
	NetworkAccessPoint.py   \
	SerialPort.py

CLEANFILES =		\
	$(BUILT_SOURCES)

DISTCLEANFILES = \
	$(CLEANFILES)

clean-local:
	rm -rf *.pyc *.pyo

