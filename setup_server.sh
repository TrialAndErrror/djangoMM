#!/bin/bash
export APP_LOCATION=$HOME

sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt install -y libpq-dev python3-dev && sudo apt install -y build-essential
sudo apt-get install -y python3-venv
sudo apt-install -y python3-pip

mkdir "$HOME/my_app/env/"
python3 -m venv ~/my_app/env/
source "$HOME/my_app/env/bin/activate"
pip install --no-input -r requirements.txt

sudo apt-get install -y python3.8-dev
sudo apt install -y libpython3-all-dev
sudo apt-get install -y gcc
pip install --no-input uwsgi

cd "$HOME/my_app/mm_project" || exit
mkdir "./mm_project/static"
python3 manage.py collectstatic

sudo apt-get install -y nginx
cd "$HOME/my_app" || exit
sudo cp mm_app.conf /etc/nginx/sites-available
sudo ln -s /etc/nginx/sites-available/mm_app.conf /etc/nginx/sites-enabled
cd ./mm_project/ || exit
mkdir media
