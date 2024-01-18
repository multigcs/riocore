
clean:
	find ./ -type d | grep "/__pycache__" | xargs -r -l rm -r
	rm -rf dist *.egg-info

format:
	find ./ -type f | grep ".py$$" | xargs -r -l isort
	find ./ -type f | grep ".py$$" | xargs -r -l black -l 200 -q

check:
	find ./ -type f | grep ".py$$" | xargs -r -l flake8 --ignore S108,S607,S605,F401,F403,W291,W503 --max-line-length 200

verilator:
	find ./riocore/ -type f | grep ".v$$" | xargs -r -l verilator --lint-only

dist:
	python3 setup.py sdist

pypi: clean dist
	twine upload --verbose dist/riocore*
