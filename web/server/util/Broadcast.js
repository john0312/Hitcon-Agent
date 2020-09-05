module.exports = class Broadcast {
    constructor(io) {
        this.io = io;
    }

    all(channel, message) {
        try {
            console.log(`channel: ${channel}, message: ${message}`);
            this.io.sockets.emit(channel, message);
        } catch(err) {
            console.error(err);
        }
    }
}
