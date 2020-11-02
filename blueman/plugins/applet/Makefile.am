bluemandir = $(pythondir)/blueman/plugins/applet

blueman_PYTHON = \
    __init__.py \
    AuthAgent.py \
    AutoConnect.py \
    Battery.py \
    ConnectionNotifier.py \
    DBusService.py \
    DhcpClient.py \
    DisconnectItems.py \
    DiscvManager.py \
    ExitItem.py \
    GameControllerWakelock.py \
    KillSwitch.py \
    Menu.py \
    NetUsage.py \
    Networking.py \
    NMDUNSupport.py \
    NMPANSupport.py \
    PowerManager.py \
    PPPSupport.py \
    RecentConns.py \
    SerialManager.py \
    ShowConnected.py \
    StatusIcon.py \
    StandardItems.py \
    TransferService.py


if HAVE_APPINDICATOR
blueman_PYTHON += AppIndicator.py
endif

CLEANFILES =		\
	$(BUILT_SOURCES)
	
DISTCLEANFILES = \
	$(CLEANFILES) 
	
clean-local:
	rm -rf *.pyc *.pyo 

