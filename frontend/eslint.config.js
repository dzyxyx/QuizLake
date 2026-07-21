import js from '@eslint/js'
import vue from 'eslint-plugin-vue'
import tseslint from '@vue/eslint-config-typescript'
import prettier from '@vue/eslint-config-prettier'

export default [
  js.configs.recommended,
  ...vue.configs['flat/recommended'],
  ...tseslint(),
  prettier,
  {
    rules: {
      'vue/multi-word-component-names': 'off',
      '@typescript-eslint/no-unused-vars': [
        'warn',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],
    },
  },
]
