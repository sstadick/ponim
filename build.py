from os import listdir
from os.path import join
from setuptools import Extension
import sys

"""
rm -rf nim_build
mkdir nim_build
nim compileToC --compileOnly -d:release -d:ssl --app:lib --opt:speed --gc:markAndSweep --nimcache:./nim_build --out:adder.so nim/adder.nim

cp  ~/.choosenim/toolchains/nim-1.0.4/lib/nimbase.h ./nim_build/nimbase.h

rm  ./nim_build/adder.json
"""

from os.path import expanduser
from os import mkdir
from shutil import copyfile, rmtree
import subprocess


def nimblize(nimbase, modules):
    """Take a list of dicsts of names and paths"""
    print(listdir("."), file=sys.stderr)
    extensions = []
    rmtree("nim_build", ignore_errors=True)
    mkdir("nim_build")
    for module in modules:
        module_dir = f"nim_build/{module['name']}_build"
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
                f"--out:{module_dir}/{module['name']}.so",
                module["path"],
            ],
            check=True,
            stderr=sys.stdout.buffer,
        )
        copyfile(
            nimbase, f"{module_dir}/nimbase.h",
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
                include_dirs=[module_dir],  # expand that path?
            )
        )
    return extensions


def build(setup_kwargs):
    """Called by poetry, the args are added to the kwargs for setup."""
    nimbase = expanduser("~") + "/.choosenim/toolchains/nim-1.0.4/lib/nimbase.h"
    setup_kwargs.update(
        {
            "ext_modules": nimblize(
                nimbase, [{"name": "adder", "path": "ponim/nim/adder.nim"}]
            ),
        }
    )
