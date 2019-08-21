import glob from "glob";
import path from "path";
import { TsconfigPathsPlugin } from "tsconfig-paths-webpack-plugin";
import webpack from "webpack";

const config: webpack.Configuration = {
    entry: () => {
        const entries: webpack.Entry = {};
        glob.sync("./src/**/*.ts").forEach(filePath => {
            entries[
                path
                    .relative("./src", filePath)
                    .replace(path.extname(filePath), "")
            ] = filePath;
        });
        console.debug(
            `Entries created:\n${JSON.stringify(entries, undefined, 4)}`,
        );
        return entries;
    },
    devtool: "inline-source-map",
    mode: "development",
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                use: "ts-loader",
                exclude: /node_modules/,
            },
        ],
    },
    resolve: {
        extensions: [".tsx", ".ts", ".js"],
        plugins: [new TsconfigPathsPlugin()],
    },
    output: {
        filename: "[name].js",
        path: path.resolve(__dirname, "dist"),
    },
};

export default config;
