
all:
	pyrexc Lib.pyx
	gcc -c -fPIC -I/usr/include/python2.5/ Lib.c
	gcc -c -fPIC -I/usr/include/bluetooth/ libblueman.c
	
	gcc -shared libblueman.o Lib.o -lbluetooth -o Lib.so
	
clean:
	rm *.o Lib.so Lib.c
