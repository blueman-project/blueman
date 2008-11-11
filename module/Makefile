
all:
	pyrexc Lib.pyx
	gcc -c -g -fPIC -I/usr/include/python2.5/ Lib.c
	gcc -c -g -fPIC -I/usr/include/bluetooth/ libblueman.c
	
	gcc -shared libblueman.o Lib.o -lbluetooth -o Lib.so
	ln -s $(CURDIR)/Lib.so ../blueman
	
clean:
	rm *.o Lib.so Lib.c
