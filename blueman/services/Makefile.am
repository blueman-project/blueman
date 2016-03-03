SUBDIRS = meta

bluemandir = $(pythondir)/blueman/services
blueman_PYTHON =     		\
	__init__.py 	   		\
	AudioSink.py	    	\
	AudioSource.py		    \
	AVRemote.py             \
	DialupNetwork.py    	\
	Functions.py		\
	GroupNetwork.py		    \
	HandsfreeGateway.py	    \
	Input.py          		\
	NetworkAccessPoint.py   \
	SerialPort.py

CLEANFILES =		\
	$(BUILT_SOURCES)

DISTCLEANFILES = \
	$(CLEANFILES)

clean-local:
	rm -rf *.pyc *.pyo

