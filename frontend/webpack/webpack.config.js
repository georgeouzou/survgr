const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
    entry: {
        procrustes: path.resolve(__dirname, '../src/scripts/procrustes.js'),
    },
    output: {
        path: path.resolve(__dirname, '../dist'),
        filename: 'js/[name].js',
    },
    plugins: [
        new MiniCssExtractPlugin({
            filename: 'css/[name].css'
        }),
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
