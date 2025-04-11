# thermine-raspi

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

protoc -I=proto -I=/usr/include --python_out=. proto/bos/v1/*.proto
python3 -m grpc_tools.protoc -I=proto -I=/usr/include --python_out=. --grpc_python_out=. proto/bos/v1/*.proto

protoc -I=proto -I=/usr/include --python_out=. proto/bos/v1/*.proto
python3 -m grpc_tools.protoc -I=proto -I=/usr/include --python_out=. --grpc_python_out=. proto/bos/v1/*.proto

## Compatibility

This is a list of firmware compatibility we tested already!

| Firmware | Miner | Version | Status |
| ---- | ---- | ---- | ---- |
| [Vnish](https://vnish-firmware.com/en/razgon-antminer-s9-s9i-s9j/) | S9 | 3.9.0 | &nbsp;&nbsp;&nbsp;&nbsp;❌ |
