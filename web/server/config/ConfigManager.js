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

const fs = require('fs');
const path = require('path');
const CONFIG_PATH = path.resolve(__dirname, './config.json');
const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));

module.exports = class ConfigManager {
    constructor() {
        // TODO: Separate different environments.
        this.config = config;
    }
    
    /**
     * Gets config value depending on string array paths.
     * @param  {string[]} paths 
     * @param  {boolean} required
     * @return {any | undefined}
     */
    getConfig(paths, required = true) {
        if (paths.length < 1) {
          console.error(`paths parameter is empty`);
          if (required) {
            throw `paths parameter is empty`;
          }
          return undefined;
        }
    
        function getPart(currentResult, nextPart) {
          let newResult = currentResult[nextPart];
          if (newResult === undefined) {
            console.error(`Config ${paths.join('.')} does not exist`);
            if (required) {
              throw `Config ${paths.join('.')} does not exist`;
            }
            return undefined;
          }
          return newResult;
        }
    
        let result = this.config;
        for (let i = 0; i < paths.length; i++) {
          result = getPart(result, paths[i]);
        }

        return result;
      }
}
