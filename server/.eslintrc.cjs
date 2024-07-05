module.exports = {
    root: true,
    env: { browser: true, es2020: true, node: true },
    extends: ["eslint:recommended", "plugin:jsx-a11y/recommended", "prettier"],
    ignorePatterns: ["dist", ".eslintrc.cjs", "node_modules"],
    parserOptions: { ecmaVersion: "latest", sourceType: "module" },
    settings: { react: { version: "18.2" } },
    plugins: [],
    rules: {},
};
