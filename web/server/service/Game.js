module.exports = class Game {
    constructor(configManager, broadcast) {
        this.configManager = configManager;
        this.broadcast = broadcast;
    }

    run(gameName, agent) {
        // Emit event notification to frontend
        const eventCallback = (data) => this.broadcast.all('event', JSON.stringify(data));
        agent.event(gameName, eventCallback);

        // Emit score list to frontend
        const scoreListCallback = (data) => this.broadcast.all('scoreList', JSON.stringify(data));
        const interval = this.configManager.getConfig(['queryScoreIntervalMillisecond']);
        setInterval(function () { agent.queryScore(gameName, null, scoreListCallback) }, interval);
    }
}
