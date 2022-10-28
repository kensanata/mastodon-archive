#!/bin/bash
# install mastodon-backup via Debian packages instead of PyPi dependencies
# © 2022 Izzy <izzysoft AT qumran DOT org>; GPL-3.0-or-later

#
# define temp dir and exit-on-error
function cleanup() {
  echo
  echo "Something went wrong, aborting."
  rm -rf $tmpdir
  exit 1
}

tmpdir=$(mktemp -d)
trap cleanup ERR


# ==============
# ===[ Main ]===
# ==============
# -----------------------------------------------------------------------------
# install Debian packages
echo
echo "Installing required Debian packages via APT. You will need to provide your"
echo "password for sudo here:"
sudo apt install python3-progress python3-mastodon

# -----------------------------------------------------------------------------
# check whether we need to update python3-mastodon
echo
echo "Let's see if your distribution had the recent version of python3-mastodon…"
mver="$(dpkg -l python3-mastodon |tail -n 1 |awk '{print $3}')"
mver="${mver%%-*}"
IFS='.'; arr=($mver); unset IFS
typeset -i vercode=${arr[2]}+${arr[1]}*100+${arr[0]}*10000
if [[ $vercode -gt 10500 ]]; then    # we need at least v1.5.1 = 10501
  echo "Found version '$mver' – all is fine!"
else
  echo "Found version '$mver' – that's too old. Let's get v1.5.1 and replace the required files."
  echo "Downloading, extracting and copying (via sudo) files"
  cd $tmpdir
  wget https://files.pythonhosted.org/packages/7c/80/f12b205fc529fff8e3245fe8e6cafb870f1783476449d3ea2a32b40928c5/Mastodon.py-1.5.1-py2.py3-none-any.whl
  unzip Mastodon.py-1.5.1-py2.py3-none-any.whl
  sudo cp mastodon/__init__.py mastodon/Mastodon.py mastodon/streaming.py /usr/lib/python3/dist-packages/mastodon
  cd - >/dev/null
  rm -rf $tmpdir
fi

# -----------------------------------------------------------------------------
# take care for the wrapper script
echo
echo "Looking for the wrapper script…"
if [[ -f ../mastodon-archive.py ]]; then
  echo "'mastodon-archive.py' already exists, skipping creation."
else
  echo "'mastodon-archive.py' not found, generating…"
  cat > ../mastodon-archive.py <<EOF
#!/usr/bin/env python3
import mastodon_archive

if __name__ == "__main__":
  mastodon_archive.main()
EOF
  chmod o+x ../mastodon-archive.py
fi

# -----------------------------------------------------------------------------
# Finito
bindir=$(dirname $(realpath .))
echo
echo "All is prepared now. You either can…"
echo "- run './mastodon-archive.py' from within '${bindir}',"
echo "- add '${bindir}' to your '\$PATH' to be able to call it from anywhere, or"
echo "- set up an 'alias mastodon-archive=\"${bindir}/mastodon-archive.py\"'"
echo "for the same purpose."
echo "Enjoy!"
echo
