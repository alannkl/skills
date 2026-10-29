const { maxUploadMb } = require('./config');

function checkSize(bytes) {
  if (bytes > maxUploadMb * 1024 * 1024) {
    const err = new Error(`file is larger than ${maxUploadMb} MB (MAX_UPLOAD_MB)`);
    err.status = 413;
    throw err;
  }
}

module.exports = { checkSize };
