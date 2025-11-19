import {FlatCompat} from '@eslint/eslintrc'
import {fileURLToPath} from 'node:url'
import globals from 'globals'
import {includeIgnoreFile} from '@eslint/compat'
import js from '@eslint/js'
import path from 'node:path'
import pluginVue from 'eslint-plugin-vue'
import vueTsEslintConfig from '@vue/eslint-config-typescript'
import parser from 'vue-eslint-parser'
import * as tsParser from '@typescript-eslint/parser'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const compat = new FlatCompat({
  baseDirectory: __dirname,
  recommendedConfig: js.configs.recommended,
  allConfig: js.configs.all
})
const gitignorePath = path.resolve(__dirname, '.gitignore')

export default [
  includeIgnoreFile(gitignorePath),
  ...pluginVue.configs['flat/essential'],
  ...vueTsEslintConfig({
    supportedScriptLangs: {
      ts: false,
      js: true
    },
    rootDir: import.meta.dirname,
  }),
  ...compat.extends(
    'eslint:recommended',
    'plugin:vue-scoped-css/vue3-recommended',
    'plugin:vue/vue3-recommended',
  ),
  {
    languageOptions: {
      globals: {
        ...globals.node,
      },
      parser: parser,
      parserOptions: {
        parser: tsParser
      }
    },
    rules: {
      '@typescript-eslint/no-explicit-any': 0,
      '@typescript-eslint/no-unsafe-function-type': 0,
      '@typescript-eslint/no-unused-vars': 2,
      'array-bracket-spacing': 2,
      eqeqeq: 2,
      'key-spacing': 2,
      'no-console': 2,
      'no-debugger': 2,
      'no-multi-spaces': 2,
      'no-trailing-spaces': 2,
      'no-unexpected-multiline': 2,
      'object-curly-spacing': 2,
      quotes: [2, 'single'],
      semi: [2, 'never'],
      'vue/arrow-spacing': 2,
      'vue/attributes-order': 2,
      'vue/block-spacing': 2,
      'vue/brace-style': 2,
      'vue/camelcase': 2,
      'vue/comma-dangle': 2,
      'vue/component-name-in-template-casing': 2,
      'vue/component-tags-order': 2,
      'vue/no-deprecated-v-bind-sync': 1,
      'vue/eqeqeq': 2,
      'vue/html-closing-bracket-newline': 2,
      'vue/html-closing-bracket-spacing': 2,
      'vue/html-end-tags': 2,
      'vue/html-indent': 2,
      'vue/html-quotes': 2,
      'vue/html-self-closing': 0,
      'vue/key-spacing': 2,
      'vue/match-component-file-name': 2,
      'vue/max-attributes-per-line': ['error', {
        singleline: {
          max: 3,
        },
        multiline: {
          max: 1,
        },
      }],
      'vue/multi-word-component-names': 0,
      'vue/multiline-html-element-content-newline': 2,
      'vue/mustache-interpolation-spacing': 2,
      'vue/no-boolean-default': 2,
      'vue/no-deprecated-destroyed-lifecycle': 1,
      'vue/no-deprecated-dollar-listeners-api': 1,
      'vue/no-deprecated-slot-attribute': 2,
      'vue/no-deprecated-v-on-native-modifier': 1,
      'vue/no-multi-spaces': 2,
      'vue/no-mutating-props': 2,
      'vue/no-restricted-syntax': 2,
      'vue/no-use-v-if-with-v-for': 2,
      'vue/no-v-html': 0,
      'vue/no-v-for-template-key-on-child': 2,
      'vue/no-v-text-v-html-on-component': 0,
      'vue/order-in-components': 2,
      'vue/require-default-prop': 2,
      'vue/require-direct-export': 2,
      'vue/require-prop-types': 2,
      'vue-scoped-css/enforce-style-type': 0,
      'vue-scoped-css/no-unused-selector': 1,
      'vue/script-indent': 2,
      'vue/singleline-html-element-content-newline': 0,
      'vue/space-infix-ops': 2,
      'vue/space-unary-ops': 2,
      'vue/this-in-template': 2,
      'vue/valid-next-tick': 1,
      'vue/valid-v-slot': ['error', {
        allowModifiers: true,
      }],
      'vue/v-bind-style': 2,
      'vue/v-on-event-hyphenation': 2,
      'vue/v-on-function-call': 2,
      'vue/v-on-style': 2,
      'vue/v-slot-style': 2,
    }
  }
]
