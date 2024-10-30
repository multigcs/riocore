
VERSION ?= $(shell grep "VERSION = " riocore/VERSION.py | cut -d'"' -f2)

clean:
	find ./ -type d | grep "/__pycache__" | xargs -r -l rm -r
	rm -rf dist *.egg-info

format:
	find ./riocore/ ./tests/ ./bin/ -type f | grep "\.py$$\|bin/" | xargs -r -l ruff format -q

check:
	find ./riocore/ ./bin/ -type f | grep ".py$$\|bin/" | xargs -r -l ruff check

unittests:
	python3 -m pytest -vv -v tests/unit/

verilator:
	find ./riocore/ -type f | grep ".v$$" | xargs -r -l verilator --lint-only

readmes:
	PYTHONPATH=. bin/rio-plugininfo -g
	PYTHONPATH=. riocore/files/update_boards_and_toolchains_readme.py

dist:
	python3 setup.py sdist

pypi: clean dist
	$(eval VERSION = v$(shell ls dist/riocore-*.tar.gz | cut -d"-" -f2 | cut -d"." -f1-3))
	twine upload --verbose dist/riocore-*.tar.gz
	git tag -a ${VERSION} -m "version ${VERSION}"
	git push origin ${VERSION}

exifclean:
	exiftool -all= riocore/boards/*/*.png
	rm -rf riocore/boards/*/*.png_original
	exiftool -all= riocore/plugins/*/*.png
	rm -rf riocore/plugins/*/*.png_original
	exiftool -all= riocore/modules/*/*.png
	rm -rf riocore/modules/*/*.png_original

pyvenv: clean dist
	python3 -m venv pyvenv
	pyvenv/bin/python -m pip install -r requirements.txt
	pyvenv/bin/python -m pip install dist/riocore*

pyvenv_test_generator:
	pyvenv/bin/python bin/rio-generator Altera10M08Eval/config.json

pyvenv_test_setup:
	pyvenv/bin/python bin/rio-setup Altera10M08Eval/config.json

docker-build-debian11_deb:
	sudo rm -rf dist/ deb_dist/
	#docker build --no-cache -t riocore_build_debian11 -f dockerfiles/Dockerfile.debian11 .
	docker build -t riocore_build_debian11 -f dockerfiles/Dockerfile.debian11 .
	docker rm riocore_build_debian11 || true
	docker run --net=host --name riocore_build_debian11 -v $(CURDIR):/usr/src/riocore -t -i riocore_build_debian11 /bin/bash -c "cd /usr/src/riocore; SETUPTOOLS_USE_DISTUTILS=stdlib python3 setup.py --command-packages=stdeb.command sdist_dsc && cd deb_dist/riocore-*/ && sed -i 's|Depends: |Depends: python3-pyqt5, python3-pyqt5.qtsvg, make, |g' debian/control && dpkg-buildpackage -rfakeroot -uc -us"
	mkdir -p debian-packages/
	cp deb_dist/*.deb debian-packages/python3-riocore_${VERSION}-bullseye_all.deb
	sudo rm -rf dist/ deb_dist/
	ls debian-packages/*deb

docker-run-debian11_deb:
	#docker build --no-cache -t riocore_debian11 -f dockerfiles/Dockerfile.debian11-min .
	docker build -t riocore_debian11 -f dockerfiles/Dockerfile.debian11-min .
	docker rm riocore_debian11 || true
	docker run --net=host -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$$DISPLAY -v $$HOME/.Xauthority:/root/.Xauthority --name riocore_debian11 -v $(CURDIR):/usr/src/riocore -t -i riocore_debian11 /bin/bash -c "cd /usr/src/riocore; apt-get install --no-install-recommends -y ./debian-packages/python3-riocore_*-bullseye_all.deb; cd ~ ; PATH=$$PATH:/opt/oss-cad-suite/bin/ rio-setup"

docker-build-debian12_deb:
	sudo rm -rf dist/ deb_dist/
	#docker build --no-cache -t riocore_build_debian12 -f dockerfiles/Dockerfile.debian12 .
	docker build -t riocore_build_debian12 -f dockerfiles/Dockerfile.debian12 .
	docker rm riocore_build_debian12 || true
	docker run --net=host --name riocore_build_debian12 -v $(CURDIR):/usr/src/riocore -t -i riocore_build_debian12 /bin/bash -c "cd /usr/src/riocore; SETUPTOOLS_USE_DISTUTILS=stdlib python3 setup.py --command-packages=stdeb.command sdist_dsc && cd deb_dist/riocore-*/ && sed -i 's|Depends: |Depends: python3-pyqt5, python3-pyqt5.qtsvg, make, |g' debian/control && dpkg-buildpackage -rfakeroot -uc -us"
	mkdir -p debian-packages/
	cp deb_dist/*.deb debian-packages/python3-riocore_${VERSION}-bookworm_all.deb
	sudo rm -rf dist/ deb_dist/
	ls debian-packages/*deb

docker-run-debian12_deb:
	#docker build --no-cache -t riocore_debian12 -f dockerfiles/Dockerfile.debian12-min .
	docker build -t riocore_debian12 -f dockerfiles/Dockerfile.debian12-min .
	docker rm riocore_debian12 || true
	docker run --net=host -v /tmp/.X12-unix:/tmp/.X12-unix -e DISPLAY=$$DISPLAY -v $$HOME/.Xauthority:/root/.Xauthority --name riocore_debian12 -v $(CURDIR):/usr/src/riocore -t -i riocore_debian12 /bin/bash -c "cd /usr/src/riocore; apt-get install --no-install-recommends -y ./debian-packages/python3-riocore_*-bookworm_all.deb; cd ~ ; PATH=$$PATH:/opt/oss-cad-suite/bin/ rio-setup"

docker-run:
	docker build -t riocore-run -f dockerfiles/Dockerfile.debian12-run .
	docker rm -f riocore-run || true
	docker run --privileged --net=host -v /tmp/.X12-unix:/tmp/.X12-unix -e DISPLAY=$$DISPLAY -v $$HOME/.Xauthority:/root/.Xauthority -v $(CURDIR):/usr/src/riocore -v $(CURDIR):/workspace -e DISPLAY=$$DISPLAY -v $$HOME/.Xauthority:/root/.Xauthority --name riocore-run -t -i riocore-run /bin/bash -c "cd /usr/src/riocore; PATH=$$PATH:/opt/oss-cad-suite/bin/ bin/rio-setup $(CONFIG)"
	docker rm -f riocore-run || true

docker-run-rpi:
	docker build -t riocore-run -f dockerfiles/Dockerfile.debian12-run-rpi .
	docker rm -f riocore-run || true
	docker run --privileged --net=host -v /tmp/.X12-unix:/tmp/.X12-unix -e DISPLAY=$$DISPLAY -v $$HOME/.Xauthority:/root/.Xauthority -v $(CURDIR):/usr/src/riocore -v $(CURDIR):/workspace -e DISPLAY=$$DISPLAY -v $$HOME/.Xauthority:/root/.Xauthority --name riocore-run -t -i riocore-run /bin/bash -c "cd /usr/src/riocore; PATH=$$PATH:/opt/oss-cad-suite/bin/ bin/rio-setup $(CONFIG)"
	docker rm -f riocore-run || true

docker-run-gowin:
	docker build -t riocore-run-gowin -f dockerfiles/Dockerfile.debian12-run-gowin .
	docker rm -f riocore-run-gowin || true
	docker run  --privileged --net=host -v /tmp/.X12-unix:/tmp/.X12-unix -e DISPLAY=$$DISPLAY -v $$HOME/.Xauthority:/root/.Xauthority -v $(CURDIR):/usr/src/riocore -v $(CURDIR):/workspace -e DISPLAY=$$DISPLAY -v $$HOME/.Xauthority:/root/.Xauthority --name riocore-run-gowin -t -i riocore-run-gowin /bin/bash -c "cd /usr/src/riocore; PATH=$$PATH:/opt/oss-cad-suite/bin/:/opt/gowin/IDE/bin/ bin/rio-setup $(CONFIG)"
	docker rm -f riocore-run-gowin || true

update:
	git pull
	git submodule update --init --recursive
	make clean
	docker rmi -f riocore-run || true
	docker rmi -f riocore-run-gowin || true
