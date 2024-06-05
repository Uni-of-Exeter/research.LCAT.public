import globals from "globals";
import pluginJs from "@eslint/js";


export default [
  {files: ["**/*.js"], languageOptions: {sourceType: "commonjs"}},
  {languageOptions: { globals: globals.browser }},
  {ignores: ["node_modules/*", "dist/*", "public/*"]},
  pluginJs.configs.recommended,
];