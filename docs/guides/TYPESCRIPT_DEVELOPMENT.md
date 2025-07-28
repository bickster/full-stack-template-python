# TypeScript Development Best Practices

This guide covers TypeScript-specific development practices for the FullStack Template to catch errors early and maintain code quality.

## Table of Contents
1. [Development Scripts](#development-scripts)
2. [Type Checking During Development](#type-checking-during-development)
3. [Common TypeScript Issues](#common-typescript-issues)
4. [Pre-commit Checks](#pre-commit-checks)
5. [IDE Configuration](#ide-configuration)
6. [Troubleshooting](#troubleshooting)

## Development Scripts

The frontend includes several scripts to help catch TypeScript errors early:

### Basic Development
```bash
# Standard development mode (no type checking)
npm run dev
```

### Development with Type Checking
```bash
# Run dev server AND type checking in watch mode concurrently
npm run dev:all

# Or run them separately in different terminals:
npm run dev           # Terminal 1: Vite dev server
npm run dev:type-check # Terminal 2: TypeScript watch mode
```

### One-time Checks
```bash
# Run type checking once
npm run type-check

# Run all checks (type-check, lint, tests)
npm run check-all

# Build (includes type checking)
npm run build
```

## Type Checking During Development

### Why Type Checking Matters

Vite's development server prioritizes speed over type safety. It only transpiles TypeScript without performing type checking, which means:

- ❌ Type errors won't prevent the app from running
- ❌ You might not see type errors until build time
- ❌ Errors can accumulate without being noticed

### Best Practices

1. **Run `npm run build` periodically** during development (every 30-60 minutes)
   - This ensures your code will build successfully
   - Catches accumulated type errors early
   - Prevents last-minute surprises before deployment

2. **Use `npm run dev:all` for active development**
   - Provides real-time type checking feedback
   - Shows errors in the terminal as you code
   - Helps maintain type safety throughout development

3. **Check before committing**
   ```bash
   # Quick check before committing
   npm run type-check

   # Comprehensive check
   npm run check-all
   ```

## Common TypeScript Issues

### 1. Type-Only Imports (verbatimModuleSyntax)

When `verbatimModuleSyntax` is enabled in `tsconfig.json`, you must use `import type` for type-only imports:

```typescript
// ❌ Wrong
import { UserType } from './types';

// ✅ Correct
import type { UserType } from './types';

// ✅ Mixed imports
import React, { type FC } from 'react';
```

### 2. Missing Type Annotations

Always add return types to functions:

```typescript
// ❌ Missing return type
const getUser = (id: string) => {
  return users.find(u => u.id === id);
};

// ✅ With return type
const getUser = (id: string): User | undefined => {
  return users.find(u => u.id === id);
};
```

### 3. Strict Null Checks

Handle potential null/undefined values:

```typescript
// ❌ Might be undefined
const userName = user.name.toUpperCase();

// ✅ Safe access
const userName = user?.name?.toUpperCase() ?? 'Unknown';
```

## Pre-commit Checks

To ensure type safety before commits, consider adding these checks to your workflow:

### Manual Pre-commit Checklist
```bash
# 1. Type check
npm run type-check

# 2. Lint check
npm run lint

# 3. Run tests
npm run test:run

# Or all at once:
npm run check-all
```

### Automated with Git Hooks (Optional)
```bash
# Install husky
npm install --save-dev husky

# Add pre-commit hook
npx husky add .husky/pre-commit "cd ui && npm run check-all"
```

## IDE Configuration

### VS Code Settings

Add to `.vscode/settings.json`:

```json
{
  "typescript.tsdk": "node_modules/typescript/lib",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "typescript.enablePromptUseWorkspaceTsdk": true
}
```

### Recommended Extensions

- TypeScript Vue Plugin (if using Vue)
- ESLint
- Prettier
- Error Lens (shows errors inline)

## Troubleshooting

### Build Fails but Dev Works

**Problem**: App runs in dev but `npm run build` fails with type errors.

**Solution**:
1. Run `npm run type-check` to see all errors
2. Fix each error systematically
3. Use `npm run dev:all` going forward

### Import Errors

**Problem**: "Cannot find module" or "Module has no exported member"

**Solution**:
1. Check if the import path is correct
2. Ensure the module is installed: `npm install`
3. For type imports, use `import type`
4. Check `tsconfig.json` paths configuration

### Type 'any' Errors

**Problem**: "Implicit any" or "no-any" errors

**Solution**:
1. Add explicit type annotations
2. Use `unknown` instead of `any` when type is truly unknown
3. Create proper interfaces for complex objects

### Performance Issues with Type Checking

**Problem**: Type checking is slow

**Solution**:
1. Use `skipLibCheck: true` in `tsconfig.json`
2. Exclude large directories (node_modules, dist)
3. Consider using project references for large codebases

## Summary

- Run `npm run build` every 30-60 minutes during development
- Use `npm run dev:all` for real-time type checking
- Always run `npm run check-all` before committing
- Configure your IDE for TypeScript support
- Fix type errors as they occur, not at build time

By following these practices, you'll catch TypeScript errors early and maintain a more robust codebase.
