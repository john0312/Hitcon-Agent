const app = require('express')();
const http = require('http').Server(app);
const io = require('socket.io')(http);
const { checkOrigin } = require('./util/middleWare');

app.use(checkOrigin);
app.get('/clients', (req, res) => {
  res.send(Object.keys(io.sockets.clients().connected))
})

io.on('connection', socket => {
  console.log(`A user connected with socket id ${socket.id}`)

  socket.broadcast.emit('user-connected', socket.id)

  socket.on('disconnect', () => {
    socket.broadcast.emit('user-disconnected', socket.id)
  })

  socket.on('nudge-client', data => {
    socket.broadcast.to(data.to).emit('client-nudged', data)
  })
})

http.listen(5000, () => {
  console.log('Listening on *:5000')
})
