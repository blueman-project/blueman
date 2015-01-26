bluemandir = $(pythondir)/blueman/main/applet
blueman_PYTHON = 		\
	BluezAgent.py		\
	Transfer.py			\
	__init__.py	

EXTRA_DIST = BluezAgent.py.in

CLEANFILES =		\
	BluezAgent.py	\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES) 

clean-local:
	rm -rf *.pyc *.pyo 

