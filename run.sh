echo "setup_venv"
case `uname` in
  Linux )
    virtualenv -ppython39 .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    ;;
  Darwin )
    virtualenv -ppython39 .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install markupsafe
    CPPFLAGS=-I/usr/local/opt/openssl/include LDFLAGS=-L/usr/local/opt/openssl/lib ARCHFLAGS="-arch x86_64" \
      pip install --global-option=build_ext --global-option="-I/usr/local/include" --global-option="-L/usr/local/lib" -r requirements.txt
      ;;
  *)
    exit 1
    ;;
esac

find . -name 'mongodb-backup' -exec rm -r {} +
python -W ignore export.py