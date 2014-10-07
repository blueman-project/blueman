SUBDIRS = meta

bluemandir = $(pythondir)/blueman/services
blueman_PYTHON =     		\
	__init__.py 	   		\
	AudioSink.py	    	\
	AudioSource.py		    \
	DialupNetwork.py    	\
	GroupNetwork.py		    \
	Handsfree.py	    	\
	Headset.py      		\
	Input.py          		\
	NetworkAccessPoint.py   \
	SerialPort.py

CLEANFILES =		\
	$(BUILT_SOURCES)

DISTCLEANFILES = \
	$(CLEANFILES)

clean-local:
	rm -rf *.pyc *.pyo

