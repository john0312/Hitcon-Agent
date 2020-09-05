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
