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

const {EventReq, QueryScoreReq} = require('./kofserver_pb.js');
const {KOFServerClient} = require('./kofserver_grpc_web_pb.js');
let client = new KOFServerClient('http://' + window.location.hostname + ':8080', null, null);

// Event
let eventStreamRequest = new EventReq();
eventStreamRequest.setGamename('game1');

let eventStream = client.event(eventStreamRequest, {});
eventStream.on('data', (response) => {
  console.log(response.getMessage());
});
eventStream.on('error', (err) => {
  console.log(`Unexpected stream error: code = ${err.code}` +
              `, message = "${err.message}"`);
});

// Scoreboard 
let scoreboardStreamRequest = new QueryScoreReq();
scoreboardStreamRequest.setGamename('game1');
scoreboardStreamRequest.setPlayername('');

let scoreboardStream = client.queryScore(scoreboardStreamRequest, {});
scoreboardStream.on('data', (response) => {
  let content = '';
  let scores = response.getScoresList();
  for(let i = 0; i < scores.length; i++) {
    let playerName = scores[i].getPlayername();
    let score = scores[i].getScore();
    let pidUptime = scores[i].getPiduptime();
    let portUptime = scores[i].getPortuptime();
    content += composeTableBody(playerName, score, pidUptime, portUptime);
  }
  document.getElementById("table_body").innerHTML = content;
});
scoreboardStream.on('error', (err) => {
  console.log(`Unexpected stream error: code = ${err.code}` +
              `, message = "${err.message}"`);
});

function composeTableBody(playerName, score, pidUptime, portUptime) {
  return `<tr><td>${playerName}</td><td>${score}</td><td>${pidUptime}</td><td>${portUptime}</td></tr>`
}
