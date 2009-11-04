
bluemandir = $(pythondir)/blueman/plugins/mechanism

if ENABLE_HAL
HAL = Hal.py 
else
HAL = 
endif

blueman_PYTHON = Config.py __init__.py Network.py Ppp.py RfKill.py $(HAL)

CLEANFILES =		\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES) 
	
clean-local:
	rm -rf *.pyc *.pyo 

