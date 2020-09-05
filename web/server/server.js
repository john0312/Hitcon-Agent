const app = require('express')();
const http = require('http').Server(app);
const io = require('socket.io')(http);
const { checkOrigin } = require('./util/middleWare');
const ConfigManager = require('./config/ConfigManager');
const Broadcast = require('./util/Broadcast');
const Agent = require('./util/Agent');
const Game = require('./service/Game');

app.use(checkOrigin);
// TODO: Remove clients 
app.get('/clients', (req, res) => {
  res.send(Object.keys(io.sockets.clients().connected))
})

// Initialize Game
let configManager = new ConfigManager();
let broadcast = new Broadcast(io);
let agent = new Agent(configManager);
let game = new Game(configManager, broadcast);
game.run("game1", agent);

const webServerPort = configManager.getConfig(['webServerPort']);
http.listen(webServerPort, () => {
  console.log(`Listening on *: ${webServerPort}`)
})
