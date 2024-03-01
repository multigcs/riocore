
clean:
	find ./ -type d | grep "/__pycache__" | xargs -r -l rm -r
	rm -rf dist *.egg-info

format:
	find ./riocore/ ./bin/ -type f | grep ".py$$\|bin/" | xargs -r -l ruff format

check:
	find ./riocore/ ./bin/ -type f | grep ".py$$\|bin/" | xargs -r -l ruff check

verilator:
	find ./riocore/ -type f | grep ".v$$" | xargs -r -l verilator --lint-only

plugin_docs:
	PYTHONPATH=. bin/rio-plugininfo -g

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
	pyvenv/bin/python bin/rio-generator Altera10M08Eval/config-test.json

