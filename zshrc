#!/usr/bin/env zsh

for zshrc_snipplet in ~/.zsh/[0-9][0-9][^.]* 
do
  source $zshrc_snipplet
done

autoload -U compinit zrecompile
compinit

do

