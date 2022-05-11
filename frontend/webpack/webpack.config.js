const path = require('path');

module.exports = {
    entry: {
        procrustes: path.resolve(__dirname, '../src/scripts/procrustes.js'),
    },
    output: {
        path: path.resolve(__dirname, '../dist'),
        filename: 'js/[name].js',
    }
};
