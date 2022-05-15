const path = require('path');
const { merge } = require('webpack-merge');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const ESLintPlugin = require('eslint-webpack-plugin');

const common_config = require('./webpack.config.common.js');

module.exports = merge(common_config,  {
    mode: 'development',
    devtool: 'inline-cheap-source-map',
    output: {
        filename: 'js/[name].js',
        chunkFilename: 'js/[name].chunk.js',
        assetModuleFilename: 'assets/[name][ext]',
    },
    plugins: [
        new MiniCssExtractPlugin({
            filename: 'css/[name].css'
        }),
        new ESLintPlugin(),
    ],
});
