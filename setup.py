#!/usr/bin/env python3
#
# SPDX-Copyright: 2017-2018 Free Software Foundation Europe e.V.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import glob
import shutil
import subprocess
from distutils import cmd
from pathlib import Path
from warnings import warn

from setuptools import setup
from setuptools.command.build_py import build_py

requirements = [
    # For parsing .reuse/dep5.
    "python-debian",
    # For downloading from spdx/spdx-license-list-data. Could maybe use
    # standard library instead?
    "requests",
    # For parsing SPDX License Expressions.
    "license-expression",
]

test_requirements = ["pytest"]


def readme_md():
    """Return contents of README.md"""
    return open("README.md").read()


def changelog_md():
    """Return contents of CHANGELOG.md"""
    return open("CHANGELOG.md").read()


class BuildTrans(cmd.Command):
    """Command for compiling the .mo files."""

    user_options = []

    def initialize_options(self):
        self.po_files = None
        self.msgfmt = None
        self.build_lib = None
        self.outputs = []

    def finalize_options(self):
        self.set_undefined_options("build", ("build_lib", "build_lib"))
        self.po_files = glob.glob("po/*.po")
        for msgfmt in ["msgfmt", "msgfmt.py", "msgfmt3.py"]:
            self.msgfmt = shutil.which(msgfmt)
            if self.msgfmt:
                break

    def run(self):
        if self.msgfmt:
            for po_file in self.po_files:
                self.announce("compiling {}".format(po_file))
                lang_dir = str(
                    Path(self.build_lib)
                    / "reuse/locale"
                    / Path(po_file).stem
                    / "LC_MESSAGES"
                )
                destination = str(Path(lang_dir) / "reuse.mo")
                compile_func = lambda msgfmt, in_file, out: subprocess.run(
                    [msgfmt, in_file, "-o", out]
                )

                self.mkpath(lang_dir)
                self.make_file(
                    po_file,
                    destination,
                    compile_func,
                    (self.msgfmt, po_file, destination),
                )
                self.outputs.append(destination)

        else:
            warn("msgfmt is not installed. Translations will not be included.")

    def get_outputs(self):
        return self.outputs


class Build(build_py):
    """Redefined build."""

    def run(self):
        self.run_command("build_trans")
        super().run()

    def get_outputs(self):
        build_trans = self.get_finalized_command("build_trans")
        return super().get_outputs() + build_trans.get_outputs()


if __name__ == "__main__":
    setup(
        name="fsfe-reuse",
        version="0.4.0a1",
        url="https://reuse.software/",
        project_urls={
            "Documentation": "https://reuse.readthedocs.io/",
            "Source": "https://github.com/fsfe/reuse-tool",
        },
        license="GPL-3.0-or-later AND Apache-2.0 AND CC0-1.0 AND CC-BY-SA-4.0",
        author="Carmen Bianca Bakker",
        author_email="carmenbianca@fsfe.org",
        description="reuse is a tool for compliance with the REUSE Initiative "
        "recommendations.",
        long_description=readme_md() + "\n\n" + changelog_md(),
        long_description_content_type="text/markdown",
        package_dir={"": "src"},
        packages=["reuse"],
        include_package_data=True,
        entry_points={"console_scripts": ["reuse = reuse._main:main"]},
        install_requires=requirements,
        tests_require=test_requirements,
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: "
            "GNU General Public License v3 or later (GPLv3+)",
            "License :: OSI Approved :: Apache Software License",
            "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
        ],
        cmdclass={"build_py": Build, "build_trans": BuildTrans},
    )
