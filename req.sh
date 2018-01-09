#!/bin/bash

set -ex

pip install --upgrade pip
pip install --upgrade setuptools
pip install "cython==0.25.2" pillow


test -n "$SKIP_CYMUNK" || pip install git+https://github.com/kivy/cymunk
test -n "$SKIP_KIVY" || pip install git+git://github.com/mahomahomaho/kivy@master2
test -n "$SKIP_KIVENT" || pip install --upgrade git+git://github.com/kivy/kivent@master#subdirectory=modules/core
test -n "$SKIP_KIVENT" || pip install --upgrade git+git://github.com/kivy/kivent@master#subdirectory=modules/cymunk

pip install pyinstaller numpy
