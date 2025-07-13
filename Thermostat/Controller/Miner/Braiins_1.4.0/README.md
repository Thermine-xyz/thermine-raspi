https://github.com/braiins/bos-plus-api
Version 1.4.0

To re-create the py files:
from same folder as "proto" folder, run
python -m grpc_tools.protoc -Iproto --python_out=. --grpc_python_out=. proto/bos/version.proto
python -m grpc_tools.protoc -Iproto/bos/v1 --python_out=. --grpc_python_out=. authentication.proto

copy the result .py files to your desired folder
rename the import to "from . import fileName" 