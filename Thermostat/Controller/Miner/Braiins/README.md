https://github.com/braiins/bos-plus-api
Version 1.6.0

To re-create the py files:
from same folder as "proto" folder, run
protoc -I=proto -I=/usr/include --python_out=proto/ --experimental_allow_proto3_optional proto/bos/*.proto
protoc -I=proto -I=/usr/include --python_out=proto/ --experimental_allow_proto3_optional proto/bos/v1/*.proto

python -m grpc_tools.protoc -Iproto --python_out=proto/ --grpc_python_out=proto/ proto/bos/*.proto
python -m grpc_tools.protoc -Iproto --python_out=proto/ --grpc_python_out=proto/ proto/bos/v1/*.proto

copy the result .py files to your desired folder
rename the import to "from . import fileName" 
