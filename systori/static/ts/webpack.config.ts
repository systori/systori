import path from "path";
import { TsconfigPathsPlugin } from "tsconfig-paths-webpack-plugin";
import webpack from "webpack";

const config: webpack.Configuration = {
    entry: ["./src/project_list.ts", "./src/goto_project.ts"],
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
