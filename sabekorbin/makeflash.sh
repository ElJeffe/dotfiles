#/bin/zsh
if pretty_make; then
  echo "Make succeeded"
  flash.sh
else
  echo "Make failed"
fi
