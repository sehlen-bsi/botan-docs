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

setup_softhsm_and_tpm_linux() {
    sudo apt-get -qq install softhsm2 libtspi-dev

    sudo chgrp -R "$(id -g)" /var/lib/softhsm/ /etc/softhsm
    sudo chmod g+w /var/lib/softhsm/tokens

    softhsm2-util --init-token --free --label test --pin 123456 --so-pin 12345678
    echo "PKCS11_LIB=/usr/lib/softhsm/libsofthsm2.so" >> "$GITHUB_ENV"
}

setup_softhsm_macos() {
    brew install softhsm
    softhsm2-util --init-token --free --label test --pin 123456 --so-pin 12345678
    echo "PKCS11_LIB=/usr/local/lib/softhsm/libsofthsm2.so" >> "$GITHUB_ENV"
}

if type -p "apt-get"; then
    # Hack to deal with https://github.com/actions/runner-images/issues/8659
    sudo rm -f /etc/apt/sources.list.d/ubuntu-toolchain-r-ubuntu-test-jammy.list
    sudo apt-get update
    sudo apt-get install -y --allow-downgrades libc6=2.35-* libc6-dev=2.35-* libstdc++6=12.3.0-* libgcc-s1=12.3.0-*

    # Normal workflow follows
    #sudo apt-get -qq update
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
        sudo apt-get -qq install doxygen python3-docutils python3-sphinx latexmk texlive-latex-extra

    elif [ "$TARGET" = "test-report" ]; then
        sudo apt-get -qq install pandoc python3-pypandoc texlive-latex-extra python3-junitparser

    fi
else
    export HOMEBREW_NO_AUTO_UPDATE=1
    export HOMEBREW_NO_INSTALLED_DEPENDENTS_CHECK=1
    brew install ccache

    if [ "$TARGET" = "shared" ]; then
        brew install boost

        # On Apple Silicon we need to specify the include directory
        # so that the build can find the boost headers.
        boostincdir=$(brew --prefix boost)/include
        echo "BOOST_INCLUDEDIR=$boostincdir" >> "$GITHUB_ENV"
        setup_softhsm_macos
    fi

    if [ -d '/Applications/Xcode_15.4.app/Contents/Developer' ]; then
        sudo xcrun xcode-select --switch '/Applications/Xcode_15.4.app/Contents/Developer'
    else
        sudo xcrun xcode-select --switch '/Applications/Xcode_15.2.app/Contents/Developer'
    fi
fi

# find the ccache cache location and store it in the build job's environment
if type -p "ccache"; then
    cache_location="$( ccache --get-config cache_dir )"
    echo "COMPILER_CACHE_LOCATION=${cache_location}" >> "${GITHUB_ENV}"
fi

echo "CCACHE_MAXSIZE=200M" >> "${GITHUB_ENV}"
