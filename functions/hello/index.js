console.log('starting function')
console.log("global =", global.isLocal);

const AWSLambda = require('aws-sdk/clients/lambda');
const archiver = require('archiver');
var Readable = require('stream').Readable
const fs = require('fs');
const { execSync } = require('child_process');

const lazyExec = (cmd) => {
  console.log("--- exec: ", cmd);
  execSync(cmd,(err, stdout, stderr) => {
    if (err) console.log("err=", err);
    if (stdout) console.log("stdout=", stdout);
    if (stderr) console.log("stderr=", stderr);
  });
  console.log("--- done exec");
}

const tmpDir = '/tmp/shortener';

exports.handle = function(e, ctx, cb) {
  console.log("Starting function execution");

  const i = 4;

  const lambda = new AWSLambda({ region: 'us-west-2' });
  console.log("Creating archiver'");
  var archive = archiver('zip', {
    zlib: { level: 9 } // Sets the compression level.
  });

  lazyExec(`rm -rf ${tmpDir}`);
  lazyExec(`cp -r . ${tmpDir}`);
  const sed = global.isLocal ? 'gsed' : 'sed';
  lazyExec(`${sed} -i 's/const i = [[:digit:]]*;/const i = ${i+1};/' ${tmpDir}/index.js`);
  process.chdir(tmpDir);

  const zipFilePath = '/tmp/newCode.zip';
  console.log("Creating stream");

  // Zip up current dir and write to zip
  var output = fs.createWriteStream(zipFilePath);
  //var output = new Readable();
  archive.pipe(output);
  console.log("globbing");
  archive.glob('./*.js');
  archive.glob('./*.json');
  archive.glob('./node_modules/**');
  console.log("finalizing");
  archive.finalize();
  //console.log("output", output);

  console.log("waiting for close...");
  output.on('close', function() {
    console.log("close callbac");
    const fileBuffer = fs.readFileSync(zipFilePath);
    const params = {
      FunctionName: 'sorter_hello',
      ZipFile: fileBuffer
    }
    lambda.updateFunctionCode(params, (err, data) => {
      console.log('data = ', data);
      console.log('err = ', err);
    })

    cb(null, { i })
  });
}
