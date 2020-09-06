# Vue and Socket.io

Use Vue, Express and Socket.io

- Runs App on port `8081`
- App communicates with Express server trough web sockets on port `8080`
- Express server communicates with Kofserver trough grpc on port `9090`

![image](https://github.com/PPPy290351/Hitcon-Agent/blob/web/web/architecture.png)

# Running

## Vue app

```bash
$ cd web

# Install dependencies
$ npm install

# Allow hosts
$ vim build/webpack.dev.conf.js
    ...
    module.exports = {
        //...
        devServer: {
            // this achieves the same effect as the first example
            // with the bonus of not having to update your config
            // if new subdomains need to access the dev server
            allowedHosts: [
            '.host.com',
            'host2.com'
            ]
        }
    };
    ...

# Modify socket.io server host 
$ vim src/main.js
    ...
    const socketServer = 'host::port'
    ...

# Serve with hot reload at host:8081
$ npm run dev
```

## Server

```bash
$ cd server

# Install dependencies
$ npm install

# Serve on host:8080
$ node server.js
```

## KofServer

```bash
$ cd kofserverMock

# Install dependencies
$ npm install

# Serve on host:9090
$ node server.js
```
