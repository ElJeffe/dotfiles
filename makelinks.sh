# !/bin/zsh

for name in zsh zshrc vim vimrc yaourtrc gitconfig
do
  if [[ ! -a ~/.$name ]]; then
    echo "create link for $name"
    ln -s ~/dotfiles/$name ~/.$name
  fi
done
