SUBDIRS =	\
	bluez	\
        config  \
	gui		\
	main	\
	plugins \
	services

bluemandir = $(pythondir)/blueman
blueman_PYTHON = 	\
	Constants.py	\
	DeviceClass.py	\
	Functions.py	\
	Sdp.py		\
	Service.py	\
	gobject.py	\
	bluemantyping.py	\
	__init__.py

CLEANFILES =		\
	Constants.py	\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES) 

EXTRA_DIST =	\
	Constants.py.in
	
clean-local:
	find . \( -name \*.pyc -o -name \*.pyo -o -name __pycache__ \) -prune -exec rm -rf {} +

