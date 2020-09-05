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
