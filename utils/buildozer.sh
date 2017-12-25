#!/bin/bash

# buildozer is installed in different user, and pip installed commands are in
# ~/bin. However, simple "sudo -u" command doesn't add it to PATH and build
# fails

export PATH=$HOME/bin:$PATH

buildozer "$@"
