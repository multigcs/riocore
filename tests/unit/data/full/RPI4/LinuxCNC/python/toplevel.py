import glob
import os
import importlib

for filename in glob.glob(os.path.join("python", "*.py")):
    name = os.path.basename(filename)[:-3]
    if name != "toplevel":
        globals()[name] = importlib.import_module(name, ".")

def __init__(self):
    pass

def __delete__(self):
    pass
