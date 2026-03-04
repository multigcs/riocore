
~/.platformio/penv/bin/pio:
	wget -O /tmp/__get-platformio.py https://raw.githubusercontent.com/platformio/platformio-core-installer/master/get-platformio.py
	python3 /tmp/__get-platformio.py
	rm -rf /tmp/__get-platformio.py

build: ~/.platformio/penv/bin/pio
	~/.platformio/penv/bin/pio run

load: ~/.platformio/penv/bin/pio
	~/.platformio/penv/bin/pio run --target=upload
