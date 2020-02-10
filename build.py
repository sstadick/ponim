from os import listdir, mkdir
from os.path import join, expanduser
from setuptools import Extension
from shutil import copyfile, rmtree
import subprocess
import sys


def nimpyize(nimbase, modules):
    """Take a list of dicts of names and paths:
    [
        {'name': 'adder', 'path': 'ponim/nim/adder.nim'},
    ]

    Additionally, you must pass in the path to 'nimbase.h' so it can be copied in.

    If you want your namespace to coexist with your pthon code, name this ponim.nim
    and then your import will look like `from ponim.nim import adder` and
    `from ponim import subtractor`. There must be a way to smooth that out in the
    __init__.py file somehow.

    Note that the file must be in the included source code dir. Currently it is
    easiest to just put this in with your python code.

    This builds a set of Extenstions, which are then passed back to setuptools.
    """
    extensions = []
    # Create a top level working dir
    rmtree("nim_build", ignore_errors=True)
    mkdir("nim_build")
    for module in modules:
        module_dir = join("nim_build", f"{module['name']}_build")
        rmtree(module_dir, ignore_errors=True)
        mkdir(module_dir)
        subprocess.run(
            [
                "nim",
                "compileToC",
                "--compileOnly",
                "-d:release",
                "-d:ssl",
                "--app:lib",
                "--opt:speed",
                "--gc:markAndSweep",
                f"--nimcache:{module_dir}",
                module["path"],
            ],
            check=True,
            stderr=sys.stdout.buffer,
        )
        copyfile(
            nimbase, join(module_dir, "nimbase.h"),
        )
        sources = []
        for c_source_file in listdir(module_dir):
            if c_source_file.endswith(".c"):
                sources.append(join(module_dir, c_source_file))
        extensions.append(
            Extension(
                name=module["name"],
                sources=sources,
                extra_compile_args=[
                    "-flto",
                    "-ffast-math",
                    "-march=native",
                    "-mtune=native",
                    "-O3",
                    "-fno-ident",
                    "-fsingle-precision-constant",
                ],
                extra_link_args=["-s"],
                include_dirs=[module_dir],  
            )
        )
    return extensions


def build(setup_kwargs):
    """Called by poetry, the args are added to the kwargs for setup."""
    nimbase = expanduser("~") + "/.choosenim/toolchains/nim-1.0.4/lib/nimbase.h"
    setup_kwargs.update(
        {
            "ext_modules": nimpyize(
                nimbase, [{"name": "adder", "path": "ponim/nim/adder.nim"}]
            ),
        }
    )
