
all: rioclient

librio.so: rio.c
	gcc -shared -fPIC -o librio.so rio.c -I.

rioclient: rioclient.c librio.so
	gcc -o rioclient rioclient.c -I. -L. -lrio

clean:
	rm -rf rioclient librio.so
