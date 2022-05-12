const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const BundleTracker = require('webpack-bundle-tracker');

module.exports = {
    entry: {
        transform: path.resolve(__dirname, '../src/scripts/transform.js'),
        procrustes: path.resolve(__dirname, '../src/scripts/procrustes.js'),
    },
    output: {
        path: path.join(__dirname, '../dist'),
        clean: true,
        publicPath: '/static/',
    },
    plugins: [
        new BundleTracker({ filename: path.resolve(__dirname, 'webpack-stats.json') }),
    ],
    module: {
        rules: [
            {
                test: /\.m?js$/,
                exclude: /node_modules/,
                use: ['babel-loader']
            },
            {
                test: /\.css$/i,
                use: [MiniCssExtractPlugin.loader, 'css-loader'],
            },
            {
                test: /\.geojson$/i,
                type: 'asset/resource',
            }
        ],
    },
};
