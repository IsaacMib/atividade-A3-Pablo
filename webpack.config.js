const path = require("path");
const TerserPlugin = require("terser-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const BundleTracker = require("webpack-bundle-tracker");

module.exports = {
    entry: ["./frontend/js/index.js"], // Arquivo de entrada
    output: {
        path: path.resolve("./frontend/bundles/"),
        filename: "[name].js",
    },
    mode: process.env.NODE_ENV === "production" ? "production" : "development",
    optimization: {
      minimize: true,
      minimizer: [new TerserPlugin()], // Minificação do JS
    },
    plugins: [
      new MiniCssExtractPlugin({ filename: "styles.[contenthash].css" }), // Para arquivos CSS, se necessário,
      new BundleTracker({ path: __dirname, filename: "webpack-stats.json" }),
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
            test: /\.s[ac]ss$/i, // Processa arquivos .scss e .sass
            use: [
                process.env.NODE_ENV === "production" ? MiniCssExtractPlugin.loader : "style-loader",
                "css-loader",
                "sass-loader",
            ],
        },
      ],
  },
};