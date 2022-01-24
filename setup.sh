sudo apt update
sudo apt install python3-pip -y

pip install -r requirements/production.txt

mkdir /media/ServerHDD

mkdir krv2/log
echo "export PYTHONPATH=/home/pi/python.krv2" >> ~/.bashrc
echo "you still need to create /etc/win-credentials with the smb credentials on the nas. See: https://linuxize.com/post/how-to-mount-cifs-windows-share-on-linux/"