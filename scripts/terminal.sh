#!/bin/env bash

#
sudo apt update

#
sudo apt install --yes git zsh curl

#
sh -c "$(curl -#fSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
