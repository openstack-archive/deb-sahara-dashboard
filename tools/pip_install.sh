#!/bin/sh

# The original script is borrowed from neutron-* repos.

# Many of horizon's repos suffer from the problem of depending on horizon,
# but it not existing on pypi.

# This wrapper for tox's package installer will use the existing package
# if it exists, else use zuul-cloner if that program exists, else grab it
# from horizon master via a hard-coded URL. That last case should only
# happen with devs running unit tests locally.

# From the tox.ini config page:
# install_command=ARGV
# default:
# pip install {opts} {packages}

ZUUL_CLONER=/usr/zuul-env/bin/zuul-cloner
BRANCH_NAME=master
horizon_installed=$(echo "import horizon" | python 2>/dev/null ; echo $?)

set -e

zuul_install () {
    if [ -x "$ZUUL_CLONER" ]; then
        export ZUUL_BRANCH=${ZUUL_BRANCH-$BRANCH}
        echo "ZUUL CLONER" > /tmp/tox_install.txt
        cwd=$(/bin/pwd)
        cd /tmp
        $ZUUL_CLONER --cache-dir \
            /opt/git \
            --branch $BRANCH_NAME \
            git://git.openstack.org \
            openstack/horizon
        cd openstack/horizon
        $install_cmd -e .
        cd "$cwd"
    else
        return 1
    fi
}

usual_install () {
    echo "PIP HARDCODE" > /tmp/tox_install.txt
    if [ -z "$HORIZON_PIP_LOCATION" ]; then
        HORIZON_PIP_LOCATION="git+https://git.openstack.org/openstack/horizon@$BRANCH_NAME#egg=horizon"
    fi
    $install_cmd -U -e ${HORIZON_PIP_LOCATION}
}

install_cmd="pip install"
if [ "$1" = "constrained" ]; then
    install_cmd="$install_cmd $2"
    shift
fi
shift

if [ $horizon_installed -eq 0 ]; then
    echo "ALREADY INSTALLED" > /tmp/tox_install.txt
    echo "Horizon already installed; using existing package"
else
    zuul_install || usual_install
fi

$install_cmd -U $*
exit $?
