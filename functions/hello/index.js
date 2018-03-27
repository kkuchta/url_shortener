console.log('starting function')
console.log("global =", global.isLocal);

const AWSLambda = require('aws-sdk/clients/lambda');
const archiver = require('archiver');
var Readable = require('stream').Readable
const fs = require('fs');
const { execSync } = require('child_process');

// Exec synchronously with some logging
const lazyExec = (cmd) => {
  console.log("--- exec: ", cmd);
  execSync(cmd,(err, stdout, stderr) => {
    if (err) console.log("err=", err);
    if (stdout) console.log("stdout=", stdout);
    if (stderr) console.log("stderr=", stderr);
  });
  console.log("--- done exec");
}

const updateThisLambdaFunction = (zipFilePath) => {
  const fileBuffer = fs.readFileSync(zipFilePath);
  const params = {
    FunctionName: 'sorter_hello',
    ZipFile: fileBuffer
  }
  const lambda = new AWSLambda({ region: 'us-west-2' });
  lambda.updateFunctionCode(params, (err, data) => {
    if (!err) console.log('Upload succeeded');
  })
};

// Zip up current dir and write to zip
const zipTo = (fileName) => {
  var archive = archiver('zip', {
    zlib: { level: 9 } // Sets the compression level.
  });

  var output = fs.createWriteStream(fileName);
  archive.pipe(output);
  archive.glob('./*.js');
  archive.glob('./*.json');
  archive.glob('./node_modules/**');
  archive.finalize();
  return output;
}

const tmpDir = '/tmp/shortener';

exports.handle = function(e, ctx, cb) {
  console.log("Starting function execution");

  const i = 4;

  lazyExec(`rm -rf ${tmpDir}`);
  lazyExec(`cp -r . ${tmpDir}`);
  const sed = global.isLocal ? 'gsed' : 'sed';
  lazyExec(`${sed} -i 's/const i = [[:digit:]]*;/const i = ${i+1};/' ${tmpDir}/index.js`);
  process.chdir(tmpDir);

  const zipFilePath = '/tmp/newCode.zip';
  zipFile = zipTo(zipFilePath);

  zipFile.on('close', function() {
    updateThisLambdaFunction(zipFilePath);

    var response = {
      statusCode: 200,
      body: JSON.stringify({ i })
    };

    cb(null, response)
  });
}
