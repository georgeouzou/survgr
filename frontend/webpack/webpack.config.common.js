const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const BundleTracker = require('webpack-bundle-tracker');

module.exports = {
    entry: {
        procrustes: path.resolve(__dirname, '../src/scripts/procrustes.js'),
    },
    output: {
        path: path.resolve(__dirname, '../dist'),
        clean: true,
        publicPath: '/static/',
    },
    plugins: [
        new BundleTracker({ filename: path.resolve(__dirname, 'webpack-stats.json') }),
    ],
    module: {
        rules: [
            {
                test: /\.css$/i,
                use: [MiniCssExtractPlugin.loader, 'css-loader'],
            }
        ],
    },
};
