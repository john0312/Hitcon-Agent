protoc: 
	protoc -I=../../kofserver/ kofserver.proto --js_out=import_style=commonjs:. --grpc-web_out=import_style=commonjs,mode=grpcwebtext:.

clean:
	rm -f ./src/kofserver_grpc_web_pb.js | rm -f ./src/kofserver_pb.js