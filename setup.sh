#! /bin/bash

# Update
sudo apt-get update
sudo apt-get upgrade

# C++
sudo apt-get install -y clang gcc g++ libboost-all-dev 

# MySQL
sudo apt-get install -y mysql-server mysql-client

#Java
sudo apt-get install -y default-jdk* gradle maven openjdk-8-jdk openjfx libgit2-dev

# Python3
sudo apt-get install -y python3-dev python3-pip python3-setuptools

# Libs
sudo pip3 install -r requirements.txt
