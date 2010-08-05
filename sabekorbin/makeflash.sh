#/bin/zsh
if pretty_make; then
  echo "Make succeeded"
  sleep 1
  flash.sh
else
  echo "Make failed"
fi
