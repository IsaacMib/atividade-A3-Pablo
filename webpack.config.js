const path = require("path");
const TerserPlugin = require("terser-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const BundleTracker = require("webpack-bundle-tracker");
const SpritesmithPlugin = require('webpack-spritesmith');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');

const isProduction = process.env.NODE_ENV === "production";

module.exports = {
    entry: ["./frontend/js/index.js"], // Arquivo de entrada
    output: {
        path: path.resolve("./frontend/bundles/"),
        filename: "[name].js",
    },
    mode: isProduction ? "production" : "development",
    optimization: {
        minimize: true,
        minimizer: [
            new TerserPlugin(),
            ...(isProduction ? [new CssMinimizerPlugin({
                minimizerOptions: {
                    preset: [
                        "default",
                        {
                            discardComments: { removeAll: true },
                        },
                    ],
                },
            })] : []), // Adiciona CssMinimizerPlugin apenas no modo produção
        ],
    },
    plugins: [
        new MiniCssExtractPlugin({
            filename: isProduction ? "styles.[contenthash].css" : "styles.css"
        }),
        new BundleTracker({ path: __dirname, filename: "webpack-stats.json" }),
        new SpritesmithPlugin({
            src: {
                cwd: `./frontend/sprites-img`,
                glob: '*.png'
            },
            target: {
                image: `./frontend/sprite/sprite.png`,
                css: `./frontend/scss/sprite.scss`
            },
            apiOptions: {
                cssImageRef: '/frontend/sprite/sprite.png'
            }
        })
    ],
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: "babel-loader",
                    options: {
                        presets: ["@babel/preset-env"],
                    },
                },
            },
            {
                test: /\.s[ac]ss$/i,
                use: [
                    MiniCssExtractPlugin.loader,
                    "css-loader",
                    {
                        loader: "sass-loader",
                        options: {
                            sassOptions: {
                                quietDeps: true,
                            },
                        },
                    },
                ],
            },
            {
                test: /\.css$/i,
                use: [
                    MiniCssExtractPlugin.loader,
                    "css-loader",
                    {
                        loader: "sass-loader",
                        options: {
                            sassOptions: {
                                quietDeps: true,
                            },
                        },
                    },
                    'postcss-loader',
                ],
            },
        ],
    },
};