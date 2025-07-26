import typescript from '@rollup/plugin-typescript';
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';

const pkg = require('./package.json');

export default [
  // Browser-friendly UMD build
  {
    input: 'src/index.ts',
    output: {
      name: 'FullStackClient',
      file: pkg.browser,
      format: 'umd',
      globals: {
        axios: 'axios'
      }
    },
    external: ['axios'],
    plugins: [
      resolve(),
      commonjs(),
      typescript({ tsconfig: './tsconfig.json' })
    ]
  },
  // CommonJS (for Node) and ES module (for bundlers) build
  {
    input: 'src/index.ts',
    external: ['axios'],
    plugins: [
      typescript({ tsconfig: './tsconfig.json' })
    ],
    output: [
      { file: pkg.main, format: 'cjs' },
      { file: pkg.module, format: 'es' }
    ]
  }
];