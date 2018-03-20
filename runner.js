const func = require('./functions/hello/index.js');
const { exec } = require('child_process');
process.chdir('functions/hello');
global.isLocal = true;
func.handle(0, 0, (first, result) => {
  console.log("result = ", result);
});
