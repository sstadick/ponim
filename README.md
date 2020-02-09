<img src="./_nim.png" width="300" height="250"/>
<img src="./_python.png" width="250" height="250"/>

# Nim + Python + Poetry = :)

Sometimes you need a little more speed. Or you need to be able to justify writing some Nim. In either case there is an easy way to bundle your Nim code in with your Python code.

In this article we will do a quick overview of how to add Nim via Poetry. Before diving in here are the tools being used:

- [Nim](https://nim-lang.org/): A fast, pythonic, compiled language
- [Nimpy](https://github.com/yglukhov/nimpy): A Nim library for exporting functions to python
- [Nimporter](https://github.com/Pebaz/nimporter): A Python library for importing .nim files
- [Poetry](https://python-poetry.org/): A build tool for Python heavily influenced by Cargo

## Install Things

You will need to install Nim, Poetry, and Nimpy. Nim and poetry include very good install instructions via the links above. For Nimpy, I recommend installing it via Nimble, which is bundled with Nim. Just run `nimble install nimpy`.

## Not Doing

Both nimpy and nimporter have excellent docs. This guide is just walking through how to hook nimporter in with poetry, not the details of nimpy, nimporter, or poetry.

## This is a Hack

But it kind of works... and Python packaging is basically all one giant gross hack, so maybe this isn't so bd?

## Begin Hack

Create a poetry project:

```bash
mkdir ponim
cd ponim
poetry init -n
```

This will create a pyproject.toml file in your current directory. Next up, lets make this a Python library!

```bash
mkdir ponim
cd ponim
touch __init__.py
touch subtractor.py
cd ../
```

We are just going to make a subtractor function in python:

```python
# In subtractor.py
def subtractor(a: int, b: int) -> int:
    return a - b
```

Now let's make that available high up the import chain:

```python
# In __init__.py
from .subtractor import subtractor
```

Cool, now let's test that all that works so far and install our package into a venv managed by Poetry:

```bash
# back in your main project dir
poetry shell
poetry install
```

And now drop into the Python REPL and test it:

```bash
python
>>> import ponim
>>> ponim.subtractor(44, 2)
42
```

It works! So let's add some Nim. 

```
poetry add nimporter
poetry install
touch ponim/adder.nim
```

And then fill out the nim file:

```nim
# In adder.nim
import nimpy

proc add(a: int, b: int): int {.exportpy.} =
    return a + b
```

And now for the magic bit, making this work seamlessly with subtractor.py. We'll update the \_\_init__.py to import the nim file and make it available in the package.

```python
import nimporter # This must come first
from .subtractor import subtractor
from .adder import adder
```

And then rebuild the package and test it out

```bash
poetry install
python
>>> import ponim
>>> ponim.subtractor(44, 2)
42
>>> ponim.adder(40, 2)
42
```

And that's it! You now have nim code bundled with your Python code! To create a wheel all you need to do is run `poetry build` and your .nim files will be included. The host system will still need to have nimpy + Nim installed, but that shouldn't be too hard to work around / improve in the future. 

There is the overhead of the nim code compiling on the first run. If you actually use this to bundle application code, you could work around that issue by running 'python -c "import ponim"' after installing the wheel. This will cache the compiled nim code in your \_\_pycache__.

So why go through all this trouble? Nim is way nicer to work with than Cython, and offers the same or better performance. There are a few wrinkles yet to be smoothed out, but this setup could easily be used with docker to deploy a python + nim application. With all the exiting things going on in Nim, like optional move semantics for performance, and the concurrency work, having this easy of an interop is amazing.

Happy Hacking!
