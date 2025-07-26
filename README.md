# thermine-raspi

## Compatibility

This is a list of firmware compatibility we tested already!

| Miner | Firmware | Version | Status |
| ---- | ---- | ---- | ---- |
| S9 | Braiins<br>[Luxor](https://docs.luxor.tech/firmware/compatibility/)<br>[Vnish](https://vnish-firmware.com/en/razgon-antminer-s9-s9i-s9j/)| [22.08.1](https://feeds.braiins-os.com/22.08.1/)<br>3.7<br>3.9.0 | &nbsp;&nbsp;&nbsp;&nbsp;✔️<br>&nbsp;&nbsp;&nbsp;&nbsp;❌<br>&nbsp;&nbsp;&nbsp;&nbsp;❌ |


## Environment config

### Python 3.9.2

install dependencies:<br />
sudo apt update<br />
sudo apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev curl libbz2-dev python3-dev<br />

Downloading Python:<br />
wget https://www.python.org/ftp/python/3.9.2/Python-3.9.2.tar.xz<br />
tar -xf Python-3.9.2.tar.xz<br />
cd Python-3.9.2<br />

Compiling and installing:<br />
./configure --enable-optimizations --prefix=/usr/local<br />
make -j$(nproc)<br />
sudo make altinstall<br />

Check it wiht:<br />
/usr/local/bin/python3.9 --version<br />

Create/mount the virtual environment:<br />
/usr/local/bin/python3.9 -m venv your_environment-env<br />
source your_environment-env/bin/activate<br />
python --version<br />

If everything worked out, you should be seeing the result as "Python 3.9.2"<br />

### PIP
curl -O https://bootstrap.pypa.io/get-pip.py<br />
python get-pip.py<br />
pip --version<br />
Result: pip 25.0.1<br />

### General packages
python3 -m pip install requests==2.32.3<br />
python3 -m pip install readerwriterlock<br />
python3 -m pip install apscheduler<br />

### gRPC: for Braiins V1
pip3 install grpcio==1.71.0 grpcio-tools==1.71.0<br />

### S9 only
pip install toml==0.10.1<br />

SSH<br />
pip install --index-url https://pypi.org/simple/ cryptography==3.3.2<br />
pip install --index-url https://pypi.org/simple/ PyNaCl==1.5.0<br />
pip install --index-url https://pypi.org/simple/ bcrypt==3.2.0<br />
pip install --index-url https://pypi.org/simple/ paramiko==3.5.1<br />

### Braiins V1
python -m pip install protobuf==5.29.4<br />
sudo apt install -y protobuf-compiler=3.12.4-1+deb11u1<br />
sudo apt install -y python3-protobuf<br />
sudo apt install -y python3-pip<br />

In case you need to re-compile the .proto files to Python, please follow as bellow:<br />
Check [README](https://github.com/igorbastosib/thermine-raspi/blob/main/Thermostat/Controller/Miner/Braiins/README.md)

## Sensor DS1820
python -m pip install w1thermsensor

In case no Sensor is need you can simulate a fake sensor OR remove/comment all related code.
For easily finding where the w1themsensor is used (and you can remove it), search for """w1thermsensor"""
