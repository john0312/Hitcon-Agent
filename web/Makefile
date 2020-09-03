protoc: 
	protoc -I=../kofserver/ kofserver.proto --js_out=import_style=commonjs:./src/ --grpc-web_out=import_style=commonjs,mode=grpcwebtext:./src/

envoy-linux:
	docker run -d -v ${CURDIR}/envoy.yaml:/etc/envoy/envoy.yaml:ro --network=host envoyproxy/envoy:v1.15.0

envoy-mac:
	docker run -d -v ${CURDIR}/envoy.yaml:/etc/envoy/envoy.yaml:ro -p 8080:8080 -p 9901:9901 envoyproxy/envoy:v1.15.0

clean:
	rm -f -r ./dist | rm -f ./src/kofserver_grpc_web_pb.js | rm -f ./src/kofserver_pb.js