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

const app = require('express')();
const http = require('http').Server(app);
const io = require('socket.io')(http);
const yaml = require('js-yaml');
const fs   = require('fs');
const { checkOrigin } = require('./util/middleWare');
const ConfigManager = require('./config/ConfigManager');
const Broadcast = require('./util/Broadcast');
const Agent = require('./util/Agent');
const GameListener = require('./service/GameListener');


try {
    app.use(checkOrigin);
    // TODO: Remove clients 
    app.get('/clients', (req, res) => {
        res.send(Object.keys(io.sockets.clients().connected))
    })
    
    // Initialize Game
    let configManager = new ConfigManager();
    let broadcast = new Broadcast(io);
    let agent = new Agent(configManager);
    
    let gameFile = yaml.safeLoad(fs.readFileSync('game.yml', 'utf8'));
    // TODO: get all game information once and store in global variable
    // Send game information to new user
    io.sockets.on('connection', function (socket) {
        socket.emit('news', {});
        // socket.emit('news', {
        //    "gameList": ["game1", "game2"], 
        //    "scoresMap": {
        //        "game1": [
        //            {"playerName": `name-1`, "score": 200, "pidUptime":50, "portUptime":40},
        //           {"playerName": `name-2`, "score": 300, "pidUptime":50, "portUptime":40}
        //        ], 
        //        "game2": [
        //            {"playerName": `name-3`, "score": 500, "pidUptime":50, "portUptime":40}
        //        ]}});
    });
    gameFile.names.forEach(gameName => {
        new GameListener(configManager, broadcast).run(gameName, agent);
    });
    
    const webServerPort = configManager.getConfig(['webServerPort']);
    http.listen(webServerPort, () => {
        console.log(`Listening on *: ${webServerPort}`);
    });
} catch (err) {
    console.error(err);
}
