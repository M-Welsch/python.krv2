echo "enabling i2c and spi interface"
sudo raspi-config nonint do_i2c 0  # yes, 0 means "activating"!
sudo raspi-config nonint do_spi 0  # yes, 0 means "activating"!

sudo apt update
sudo apt install python3-pip cifs-utils libopenjp2-7 -y

mkdir krv2/log

pip install -r requirements/production.txt

cd ..
git clone https://github.com/M-Welsch/MishMash.git
cd MishMash
sudo python setup.py install

sudo mkdir /media/NASHDD

# install bluetooth stuff
cd /home/pi
git clone https://github.com/nicokaiser/rpi-audio-receiver.git  # from https://www.tutonaut.de/raspberry-pi-als-bluetooth-airplay-empfaenger-kombi/#comment-252880
cd rpi-audio-receiver
sudo ./install.sh  # interactively

echo 'export PYTHONPATH="${PYTHONPATH}:/home/pi/python.krv2"' >> ~/.bashrc
echo 'alias pytest-sw="python -m pytest -m \"not performance and not onraspi\""' >> ~/.bashrc
echo "you still need to create /etc/win-credentials with the smb credentials on the nas. See: https://linuxize.com/post/how-to-mount-cifs-windows-share-on-linux/"