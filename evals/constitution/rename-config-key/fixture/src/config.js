const defaults = require('../config/default.json');

module.exports = {
  port: Number(process.env.PORT || defaults.port),
  uploadDir: process.env.UPLOAD_DIR || defaults.uploads.dir,
  maxUploadMb: Number(process.env.MAX_UPLOAD_MB || defaults.uploads.MAX_UPLOAD_MB),
};
