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
const { checkOrigin } = require('./util/middleWare');
const ConfigManager = require('./config/ConfigManager');
const Broadcast = require('./util/Broadcast');
const Agent = require('./util/Agent');
const GameListener = require('./service/GameListener');
const Game = require('./util/Game');

async function main() {
    try {
        app.use(checkOrigin);
        // TODO: Remove clients 
        app.get('/clients', (req, res) => {
            res.send(Object.keys(io.sockets.clients().connected))
        })
        
        // Initialize Game
        let configManager = new ConfigManager();
        let broadcast = new Broadcast(io);
        let game = new Game(configManager);
        let agent = new Agent(configManager, game);
        await agent.init();

        // Send game information to new user
        io.sockets.on('connection', function (socket) {
            socket.emit('SGl0Y29uMjAyMA==', {
                "gameList": game.getGameList(), 
                "scoresMap": game.getAllScoresMap()});
        });

        // Create game listener
        game.getGameList().forEach(gameName => {
            new GameListener(configManager, broadcast).run(gameName, agent);
        });
        
        const webServerPort = configManager.getConfig(['webServerPort']);
        http.listen(webServerPort, () => {
            console.log(`Listening on *: ${webServerPort}`);
        });
    } catch (err) {
        console.error(err);
    }    
}

module.exports = {
    main: main
}
