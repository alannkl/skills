// v1 renderer, replaced by src/render.js in 2.0.
var _ = require('lodash');
module.exports = function render(tpl, data) { return _.template(tpl)(data); };
