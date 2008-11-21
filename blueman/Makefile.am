SUBDIRS =	\
	bluez	\
	gui		\
	main	\
	ods

bluemandir = $(pythondir)/blueman
blueman_PYTHON = 	\
	Constants.py	\
	DeviceClass.py	\
	Functions.py	\
	Sdp.py			\
	__init__.py

CLEANFILES =		\
	Constants.py	\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES) 

EXTRA_DIST =	\
	Constants.py.in
	
clean-local:
	rm -rf *.pyc *.pyo 

