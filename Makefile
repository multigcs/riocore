
clean:
	find ./ -type d | grep "/__pycache__" | xargs -r -l rm -r
	rm -rf dist *.egg-info

format:
	find ./riocore/ ./bin/ -type f | grep ".py$$" | xargs -r -l isort
	find ./riocore/ ./bin/ -type f | grep ".py$$" | xargs -r -l black -l 200 -q

check:
	find ./riocore/ ./bin/ -type f | grep ".py$$" | xargs -r -l flake8 --ignore S108,S607,S605,F401,F403,W291,W503 --max-line-length 200

verilator:
	find ./riocore/ -type f | grep ".v$$" | xargs -r -l verilator --lint-only

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

