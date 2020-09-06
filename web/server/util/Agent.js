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

module.exports = class Agent {
    constructor(configManager) {
        const PROTO_PATH = path.resolve(__dirname, configManager.getConfig(['protoPath']));
        try {
            this.client = new GRPCClient(PROTO_PATH, 
                configManager.getConfig(['packageService']), 
                configManager.getConfig(['theService']), 
                configManager.getConfig(['kofServer']));
        } catch(err) {
            console.error(err);
        }
    }

    event(gameName, callback) {
        let req = {gameName: gameName,};
        try {
            const stream = this.client.eventStream(req);
            stream.on('data', (data) => {
                console.log(data);
                callback(data);
            });
            stream.on('error', (err) => {
                console.log(`Unexpected stream error: code = ${err.code} , message = "${err.message}"`);
            });   
        } catch(err) {
            console.error(err);
        }
    }

    queryScore(gameName, playerName, callback) {
        let req = {gameName: gameName, playerName: playerName, };
        try {
            this.client.queryScoreAsync(req, (err, res) => {
                if(err) {
                    throw err;
                }
                console.log('Service response ', res);
                callback(res);
            });   
        } catch(err) {
            console.error(err);
        }     
    }
}
