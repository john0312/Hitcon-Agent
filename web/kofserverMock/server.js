/**
 *
 * Copyright 2018 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

const path = require('path');
const PROTO_PATH = path.resolve(__dirname, '../../kofserver/kofserver.proto');
const assert = require('assert');
const async = require('async');
const _ = require('lodash');
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
let packageDefinition = protoLoader.loadSync(
    PROTO_PATH,
    {keepCase: true,
     longs: String,
     enums: String,
     defaults: true,
     oneofs: true
    });
let protoDescriptor = grpc.loadPackageDefinition(packageDefinition);
let kofserver = protoDescriptor.kofserver;

/**
 * @param {!Object} call
 */
function repeatEvent(call) {
  let senders = [];
  function sender(name) {
    return (callback) => {
      call.write({
        message: 'Event! ' + name
      });
      _.delay(callback, 1000); // in ms
    };
  }
  for (let i = 0; i < 100000; i++) {
    senders[i] = sender(i);
  }
  async.series(senders, () => {
    call.end();
  });
}

let array = [];
function queryScore(call, callback) {
  let random = Math.random() * 1000;
  array.push({"playerName": `name-${array.length}`, "score": random, "pidUptime":50, "portUptime":40})
  callback(null, {
    reply: { "error" : 0},
    scores: array
  });
}

/**
 * @return {!Object} gRPC server
 */
function getServer() {
  let server = new grpc.Server();
  server.addService(kofserver.KOFServer.service, {
    event: repeatEvent,
    queryScore: queryScore
  });
  return server;
}

if (require.main === module) {
  let server = getServer();
  server.bindAsync(
    '0.0.0.0:9090', grpc.ServerCredentials.createInsecure(), (err, port) => {
      assert.ifError(err);
      server.start();
  });
}

exports.getServer = getServer;
