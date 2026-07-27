---
name: bootstrap
description: Bootstrap a new software project from scratch to a verified, runnable baseline.
---

Infer the project type and material constraints from the request and environment. Use the ecosystem's official initializer, ask only about choices that would change the project shape and cannot be inferred, and install the latest dependency versions.

## Web defaults

### Frontend

- Scaffold Vue 3 with create-vue. Add Vue Router, Pinia, and VueUse only when the project needs them.
- Use Tailwind CSS for atomic styling.

### Backend

- Use Hono, with Drizzle when persistence is required.

### Tooling

- Use pnpm for package management.
- Use oxlint for linting and oxfmt for formatting.

Keep the bootstrap minimal and coherent: remove unused starter content and leave out speculative dependencies.

The bootstrap is complete when the primary entry point starts or the project builds, and every configured lint, typecheck, test, and build command passes. Hand off with the chosen stack and verification results.
