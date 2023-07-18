#!/bin/bash

# GitHub Actions setup script for Botan build
#
# (C) 2015,2017 Simon Warta
# (C) 2016,2017,2018,2020 Jack Lloyd
#
# Botan is released under the Simplified BSD License (see license.txt)

command -v shellcheck > /dev/null && shellcheck "$0" # Run shellcheck on this if available

set -ex

TARGET="$1"
ARCH="$2"

SCRIPT_LOCATION=$(cd "$(dirname "$0")"; pwd)

setup_softhsm_and_tpm_linux() {
    sudo apt-get -qq install softhsm2 libtspi-dev

    sudo chgrp -R "$(id -g)" /var/lib/softhsm/ /etc/softhsm
    sudo chmod g+w /var/lib/softhsm/tokens

    softhsm2-util --init-token --free --label test --pin 123456 --so-pin 12345678
    echo "PKCS11_LIB=/usr/lib/softhsm/libsofthsm2.so" >> "$GITHUB_ENV"
}

if type -p "apt-get"; then
    sudo apt-get -qq update
    sudo apt-get -qq install ccache

    setup_softhsm_and_tpm_linux

    if [ "$TARGET" = "shared" ] ; then
        sudo apt-get -qq install libboost-dev

    elif [ "$TARGET" = "coverage" ]; then
        sudo apt-get -qq install lcov python3-coverage
        curl -L https://coveralls.io/coveralls-linux.tar.gz | tar -xz -C /usr/local/bin

        sudo apt-get -qq install libboost-dev

        echo "$HOME/.local/bin" >> "$GITHUB_PATH"

    elif [ "$TARGET" = "pdf_docs" ]; then
        sudo apt-get -qq install doxygen python-docutils python3-sphinx latexmk texlive-latex-extra
    fi
else
    export HOMEBREW_NO_AUTO_UPDATE=1
    brew install ccache

    if [ "$TARGET" = "shared" ]; then
        brew install boost
    fi

    sudo xcrun xcode-select --switch '/Applications/Xcode_14.3.1.app/Contents/Developer'
fi

# find the ccache cache location and store it in the build job's environment
if type -p "ccache"; then
    cache_location="$( ccache --get-config cache_dir )"
    echo "COMPILER_CACHE_LOCATION=${cache_location}" >> "${GITHUB_ENV}"
fi

echo "CCACHE_MAXSIZE=200M" >> "${GITHUB_ENV}"
