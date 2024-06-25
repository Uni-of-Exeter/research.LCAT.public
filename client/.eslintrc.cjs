module.exports = {
    root: true,
    env: { browser: true, es2020: true, node: true },
    extends: [
        "eslint:recommended",
        "plugin:react/recommended",
        "plugin:react-hooks/recommended",
        "plugin:jsx-a11y/recommended",
        "prettier",
    ],
    ignorePatterns: ["/dist", ".eslintrc.cjs", "/node_modules", "/src/images/**"],
    parserOptions: { ecmaVersion: "latest", sourceType: "module" },
    settings: { react: { version: "18.2" } },
    plugins: ["react-refresh", "simple-import-sort"],
    rules: {
        "react/jsx-no-target-blank": "off",
        "react-refresh/only-export-components": ["warn", { allowConstantExport: true }],
        "react/react-in-jsx-scope": "off",
        "simple-import-sort/imports": "error",
        "simple-import-sort/exports": "error",
    },
};
