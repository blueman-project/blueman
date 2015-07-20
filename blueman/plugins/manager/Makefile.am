SUBDIRS =	


bluemandir = $(pythondir)/blueman/plugins/manager

blueman_PYTHON = \
	Services.py \
	__init__.py

if HAVE_PULSEAUDIO
blueman_PYTHON += PulseAudioProfile.py
endif

CLEANFILES = \
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES) 
	
clean-local:
	rm -rf *.pyc *.pyo 

