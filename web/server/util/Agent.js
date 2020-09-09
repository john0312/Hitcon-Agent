/**
 * Copyright (c) 2020 HITCON Agent Contributors
 * See CONTRIBUTORS file for the list of HITCON Agent Contributors

 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:

 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.

 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

const path = require('path');
const GRPCClient = require('node-grpc-client');
const vsprintf = require('sprintf-js').vsprintf;

const protoEnum = {
    GameEventType: { 
        EVT_NA: "EVT_NA",
        PROC_CREATE: "PROC_CREATE",
        PROC_TERMINATE: "PROC_TERMINATE",
        GAME_NOT_FOUND: "GAME_NOT_FOUND",
        PLAYER_START_GAIN: "PLAYER_START_GAIN",
        PLAYER_STOP_GAIN: "PLAYER_STOP_GAIN"
    },
    GainReason: { REASON_NONE: "REASON_NONE", REASON_PORT: "REASON_PORT", REASON_PID: "REASON_PID" },
    ErrorCode: { 
        ERROR_NONE: "ERROR_NONE",
        ERROR_NOT_IMPLEMENTED: "ERROR_NOT_IMPLEMENTED",
        ERROR_CREATE_GAME: "ERROR_CREATE_GAME",
        ERROR_GAME_NOT_FOUND: "ERROR_GAME_NOT_FOUND",
        ERROR_USER_ALREADY_EXISTS: "ERROR_USER_ALREADY_EXISTS",
        ERROR_GAME_ALREADY_EXISTS: "ERROR_GAME_ALREADY_EXISTS",
        ERROR_GAME_NOT_ALLOW: "ERROR_GAME_NOT_ALLOW",
        ERROR_GAME_NOT_RUNNING: "ERROR_GAME_NOT_RUNNING",
        ERROR_USER_NOT_REGISTERED: "ERROR_USER_NOT_REGISTERED",
        ERROR_AGENT_PROBLEM: "ERROR_AGENT_PROBLEM",
        ERROR_PLAYER_NOT_FOUND: "ERROR_PLAYER_NOT_FOUND"
    },
}

module.exports = class Agent {
    constructor(configManager, game) {
        const PROTO_PATH = path.resolve(__dirname, configManager.getConfig(['protoPath']));
        try {
            this.configManager = configManager;
            this.game = game;
            this.client = new GRPCClient(PROTO_PATH, 
                this.configManager.getConfig(['packageService']), 
                this.configManager.getConfig(['theService']), 
                this.configManager.getConfig(['kofServer']));
        } catch(err) {
            console.error(err);
        }
    }

    async init() {
        try{
            let tasks = [];
            this.game.getGameList().forEach(gameName => {
                tasks.push(this.promiseQueryScore(gameName));
            });
            await Promise.all(tasks).then(results => {
                let final = results.filter(item => !!item);
                final.forEach(item => {
                    this.game.insertScoresMap(item.gameName, item.message.scores);
                })
            }).catch(err => {
                console.error(err);
            })
        } catch(err) {
            console.error(err);
        }
    }

    event(gameName, callback) {
        let req = {gameName: gameName,};
        try {
            const stream = this.client.gameEventListenerStream(req);
            stream.on('data', (data) => {
                let message = composeMessage(this.configManager.getConfig(['message']), data);
                if(message !== '') {
                    let result = {
                        gameName: gameName,
                        message: message
                    };
                    console.log(result);
                    callback(result);
                }
            });
            stream.on('error', (err) => {
                console.log(`Unexpected stream error: code = ${err.code} , message = "${err.message}"`);
            });   
        } catch(err) {
            console.error(err);
        }
    }

    queryScore(gameName, callback) {
        let req = {gameName: gameName, playerName: null, };
        try {
            this.client.queryScoreAsync(req, (err, res) => {
                let isError = err || !res;
                if(isError) {
                    console.error(err);
                    return;
                }
                let errorCode = res.reply.error;
                if(errorCode === protoEnum.ErrorCode.ERROR_NONE) {
                    this.game.insertScoresMap(gameName, res.scores);
                    let result = {
                        gameName: gameName,
                        message: res
                    };
                    console.log(`GameName: ${gameName}, Score List length: ${result.message.scores.length}`);
                    callback(result);
                }
            });   
        } catch(err) {
            console.error(err);
        }     
    }

    promiseQueryScore(gameName) {
        let req = {gameName: gameName, playerName: null, };
        return new Promise((resolve, reject ) => { 
            try { 
                this.client.queryScoreAsync(req, (err, res) => {
                    let isError = err || !res;
                    if(isError) {
                        reject(err);
                        return;
                    }
                    let errorCode = res.reply.error;
                    if(errorCode === protoEnum.ErrorCode.ERROR_NONE) {
                        let result = {
                            gameName: gameName,
                            message: res
                        };
                        console.log(`GameName: ${gameName}, Score List length: ${result.message.scores.length}`);
                        resolve(result); 
                    }
                });
            } catch(err) {
                reject(err);
            }
        })  
    }
}

function composeMessage(message, data) {
    let lang = message.mode;
    let eventType = data.eventType;
    if(eventType === protoEnum.GameEventType.GAME_NOT_FOUND) return '';

    let pid = data.info.pid;
    let cmdline = data.info.cmdline;
    let playerName = data.playerName;
    let playerMsg = `by ${playerName}`;
    let gainReason = data.gainReason;
    switch (eventType) {
        case protoEnum.GameEventType.PROC_CREATE:
            return vsprintf(message[lang]['PROC_CREATE'], [pid, cmdline, playerMsg]);
        case protoEnum.GameEventType.PROC_TERMINATE:
            return vsprintf(message[lang]['PROC_TERMINATE'], [pid, cmdline, playerMsg]);
        case protoEnum.GameEventType.PLAYER_START_GAIN:
            return vsprintf(message[lang]['PLAYER_START_GAIN'], [playerName, reason2Str(gainReason)]);
        case protoEnum.GameEventType.PLAYER_STOP_GAIN:
            return vsprintf(message[lang]['PLAYER_STOP_GAIN'], [playerName, reason2Str(gainReason)]);
        default:
            return '';
    }
}

function reason2Str(r) {
    if(r === protoEnum.GainReason.REASON_PORT) {
        return "port";
    } else if(r === protoEnum.GainReason.REASON_PID) {
        return "process";
    }
    return "none";
}
