#/bin/zsh
if pretty_make.py; then
  echo "Make succeeded"
  flash.sh
else
  echo "Make failed"
fi
