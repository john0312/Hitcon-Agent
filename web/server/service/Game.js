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