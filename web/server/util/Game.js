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

const yaml = require('js-yaml');
const fs   = require('fs');
const path = require('path');

module.exports = class Game {
    constructor(configManager) {
        this.scoresMap = {};
        this.configManager = configManager;
        try {
            const GAME_PATH = path.resolve(__dirname, this.configManager.getConfig(['gameFile']));
            this.gameList = yaml.safeLoad(fs.readFileSync(GAME_PATH, 'utf8')).names;
        } catch(err) {
            this.gameList = [];
            console.error(err);
        }
    }
    // TODO: Implement Lock
    insertScoresMap(gameName, scores) {
        this.scoresMap[gameName] = scores;
    }

    getGameList() {
        return this.gameList;
    }

    getScoresMap(gameName) {
        return this.scoresMap[gameName] ? this.scoresMap[gameName] : [];
    }

    getAllScoresMap() {
        return this.scoresMap;
    }
}
