sudo apt update
sudo apt install python3-pip python3-virtualenv

virtualenv krv2_venv

source krv2_venv/bin/activate

pip install -r requirements/production.txt

cd ..
git clone https://github.com/M-Welsch/MishMash.git
cd MishMash
sudo python setup.py install