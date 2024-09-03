
clean:
	find ./ -type d | grep "/__pycache__" | xargs -r -l rm -r
	rm -rf dist *.egg-info

format:
	find ./riocore/ ./tests/ ./bin/ -type f | grep ".py$$\|bin/" | xargs -r -l ruff format -q

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

pyvenv: clean dist
	python3 -m venv pyvenv
	pyvenv/bin/python -m pip install -r requirements.txt
	pyvenv/bin/python -m pip install dist/riocore*

pyvenv_test_generator:
	pyvenv/bin/python bin/rio-generator Altera10M08Eval/config.json

pyvenv_test_setup:
	pyvenv/bin/python bin/rio-setup Altera10M08Eval/config.json

docker-build-debian11_deb:
	$(eval VERSION = v$(shell ls dist/riocore-*.tar.gz | cut -d"-" -f2 | cut -d"." -f1-3))
	sudo rm -rf dist/ deb_dist/
	#docker build --no-cache -t riocore_build_debian11 -f dockerfiles/Dockerfile.debian11 .
	docker build -t riocore_build_debian11 -f dockerfiles/Dockerfile.debian11 .
	docker rm riocore_build_debian11 || true
	docker run --net=host --name riocore_build_debian11 -v $(CURDIR):/usr/src/riocore -t -i riocore_build_debian11 /bin/bash -c "cd /usr/src/riocore; SETUPTOOLS_USE_DISTUTILS=stdlib python3 setup.py --command-packages=stdeb.command sdist_dsc && cd deb_dist/riocore-*/ && dpkg-buildpackage -rfakeroot -uc -us"
	mkdir -p debian-packages/
	cp deb_dist/*.deb debian-packages/python3-riocore_${VERSION}-bullseye_amd64.deb
	sudo rm -rf dist/ deb_dist/
	ls debian-packages/*deb

docker-run-debian11_deb:
	$(eval VERSION = v$(shell ls dist/riocore-*.tar.gz | cut -d"-" -f2 | cut -d"." -f1-3))
	#docker build --no-cache -t riocore_debian11 -f dockerfiles/Dockerfile.debian11-min .
	docker build -t riocore_debian11 -f dockerfiles/Dockerfile.debian11-min .
	docker rm riocore_debian11 || true
	docker run --net=host -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$$DISPLAY -v $$HOME/.Xauthority:/root/.Xauthority --name riocore_debian11 -v $(CURDIR):/usr/src/riocore -t -i riocore_debian11 /bin/bash -c "cd /usr/src/riocore; apt-get install --no-install-recommends -y ./debian-packages/python3-riocore_*-bullseye_amd64.deb; cd ~ ; rio-setup"
