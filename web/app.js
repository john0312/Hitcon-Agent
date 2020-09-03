const express = require('express')
const app = express()
const port = 8081

app.use('/static', express.static('static'));
app.use('/dist', express.static('dist'));
app.get('/', (req, res) => {
    res.sendfile(__dirname + '/index.html');
})

app.listen(port, () => {
    console.log(`App listening at prot: ${port}`)
})
