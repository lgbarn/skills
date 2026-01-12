# Skill Examples

Complete working examples of well-structured Claude Code skills.

---

## Example 1: Simple Utility Skill (Commit Helper)

A minimal skill for creating git commits with consistent formatting.

```markdown
---
name: commit
description: Review changes and create a git commit with a well-formatted message. Use when ready to commit changes, need help writing commit messages, or want to review staged changes before committing. Triggers: "commit", "git commit", "commit changes", "commit this".
allowed-tools: Bash(git:*)
---

# Commit Helper

Create well-formatted git commits.

## Workflow

1. Run `git status` to see changed files
2. Run `git diff` to review changes
3. Stage appropriate files with `git add`
4. Create commit with descriptive message

## Commit Message Format

```
<type>: <short description>

<optional body explaining why>

🤖 Generated with Claude Code
```

**Types**: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

## Example

```bash
git add src/feature.ts
git commit -m "feat: add user authentication

Implements OAuth2 flow for secure login.

🤖 Generated with Claude Code"
```
```

---

## Example 2: Code Generation Skill

A skill for generating React components following project conventions.

```markdown
---
name: react-component
description: Generate React components following project conventions with TypeScript, tests, and Storybook stories. Use when creating new components, adding component variants, or scaffolding component structure. Triggers: "create component", "new component", "React component", "generate component".
allowed-tools: Read, Write, Edit, Glob, Grep
---

# React Component Generator

Generate consistent React components with all supporting files.

## Quick Start

When asked to create a component:

1. Check existing components in `src/components/` for patterns
2. Generate component file with TypeScript
3. Generate test file with React Testing Library
4. Generate Storybook story (if project uses Storybook)

## File Structure

```
src/components/ComponentName/
├── ComponentName.tsx      # Main component
├── ComponentName.test.tsx # Tests
├── ComponentName.stories.tsx # Storybook (optional)
├── index.ts               # Re-export
└── types.ts               # TypeScript interfaces (if complex)
```

## Component Template

```tsx
import React from 'react';
import styles from './ComponentName.module.css';

interface ComponentNameProps {
  /** Primary content */
  children?: React.ReactNode;
  /** Additional CSS classes */
  className?: string;
}

export const ComponentName: React.FC<ComponentNameProps> = ({
  children,
  className,
}) => {
  return (
    <div className={`${styles.root} ${className ?? ''}`}>
      {children}
    </div>
  );
};
```

## Test Template

```tsx
import { render, screen } from '@testing-library/react';
import { ComponentName } from './ComponentName';

describe('ComponentName', () => {
  it('renders children', () => {
    render(<ComponentName>Test content</ComponentName>);
    expect(screen.getByText('Test content')).toBeInTheDocument();
  });
});
```

## Before Generating

Always read these files first to match project patterns:
- `src/components/*/` - existing component structure
- `tsconfig.json` - TypeScript configuration
- `package.json` - available dependencies
```

---

## Example 3: Documentation Lookup Skill

A read-only skill for finding and explaining project documentation.

```markdown
---
name: docs-lookup
description: Find and explain project documentation, architecture decisions, and code patterns. Use when asking about how things work, why decisions were made, or where to find information. Triggers: "how does", "where is", "explain", "find docs", "documentation".
allowed-tools: Read, Glob, Grep
---

# Documentation Lookup

Find and explain project documentation without making changes.

## Documentation Locations

Check these locations for relevant docs:

| Location | Content |
|----------|---------|
| `README.md` | Project overview, setup |
| `docs/` | Detailed documentation |
| `ARCHITECTURE.md` | System design |
| `CONTRIBUTING.md` | Development guidelines |
| `CHANGELOG.md` | Version history |
| `*.md` in directories | Feature-specific docs |

## Search Strategy

1. **Direct match**: Look for file with topic name
2. **Grep search**: Search for keywords in markdown files
3. **Code comments**: Check inline documentation
4. **Type definitions**: Review interfaces/types for API docs

## Response Format

When explaining documentation:

1. **Quote relevant sections** directly
2. **Provide file path** for reference
3. **Summarize key points** concisely
4. **Link related docs** if they exist

## Example Queries

- "How does authentication work?" → Search for auth, login, session
- "Where are the API endpoints defined?" → Look in routes/, api/
- "Explain the database schema" → Check models/, schema/, migrations/
```

---

## Example 4: Multi-File Skill with Progressive Disclosure

A larger skill that splits content across multiple files.

**Directory structure:**
```
api-client-generator/
├── SKILL.md          # Main entry (~200 lines)
├── TEMPLATES.md      # Code templates
├── PATTERNS.md       # Design patterns
└── VALIDATION.md     # Error handling patterns
```

**SKILL.md:**
```markdown
---
name: api-client-generator
description: Generate type-safe API client code from OpenAPI/Swagger specifications. Use when creating API clients, updating clients after spec changes, or adding new endpoint support. Triggers: "generate client", "API client", "OpenAPI", "Swagger", "REST client".
allowed-tools: Read, Write, Edit, Glob, Grep, WebFetch
---

# API Client Generator

Generate type-safe TypeScript API clients from OpenAPI specs.

## Quick Start

1. Locate OpenAPI spec (`.json` or `.yaml`)
2. Generate TypeScript interfaces for schemas
3. Generate client methods for endpoints
4. Add error handling and retry logic

## Workflow

```
1. Read OpenAPI spec
2. Extract schemas → Generate types (see TEMPLATES.md)
3. Extract endpoints → Generate methods (see PATTERNS.md)
4. Add error handling (see VALIDATION.md)
```

## Generated Structure

```
src/api/
├── types.ts     # Generated interfaces
├── client.ts    # API client class
├── endpoints/   # Per-resource modules
└── errors.ts    # Error types
```

## Endpoint Method Pattern

```typescript
async getUser(id: string): Promise<User> {
  const response = await this.fetch(`/users/${id}`);
  return this.handleResponse<User>(response);
}
```

## Supporting Files

- [TEMPLATES.md](TEMPLATES.md) - Code generation templates
- [PATTERNS.md](PATTERNS.md) - Client architecture patterns
- [VALIDATION.md](VALIDATION.md) - Error handling and validation
```

---

## Example 5: Workflow Automation Skill

A skill that orchestrates multiple tools for a complex workflow.

```markdown
---
name: pr-review
description: Review pull requests by analyzing code changes, checking for issues, and providing structured feedback. Use when reviewing PRs, checking code quality, or preparing merge feedback. Triggers: "review PR", "pull request review", "check PR", "PR feedback".
allowed-tools: Read, Grep, Glob, Bash(git:*, gh:*)
---

# Pull Request Review

Structured PR review workflow with quality checks.

## Review Workflow

### 1. Gather Context

```bash
# Get PR details
gh pr view <number> --json title,body,files,commits

# Get changed files
gh pr diff <number> --name-only

# Get full diff
gh pr diff <number>
```

### 2. Analyze Changes

For each changed file:
- Read the full file for context
- Identify the type of change (new, modified, deleted)
- Check for patterns that need review

### 3. Quality Checks

| Check | What to Look For |
|-------|------------------|
| **Breaking changes** | API signature changes, removed exports |
| **Security** | Hardcoded secrets, SQL injection, XSS |
| **Performance** | N+1 queries, missing indexes, large loops |
| **Testing** | New code has tests, edge cases covered |
| **Types** | Proper TypeScript, no `any` abuse |

### 4. Provide Feedback

Structure feedback as:

```markdown
## Summary
Brief overview of the PR

## Strengths
- What's done well

## Suggestions
- Areas for improvement

## Required Changes
- Must fix before merge

## Questions
- Clarifications needed
```

## Commands Reference

```bash
# Approve PR
gh pr review <number> --approve

# Request changes
gh pr review <number> --request-changes --body "..."

# Add comment
gh pr review <number> --comment --body "..."
```
```

---

## Example 6: Platform-Specific Skill

A skill that targets a specific technology platform.

```markdown
---
name: nextjs-app
description: Create and modify Next.js App Router applications with Server Components, Server Actions, and modern patterns. Use when building Next.js features, debugging routing issues, or implementing data fetching. Triggers: "Next.js", "App Router", "Server Component", "Server Action", "RSC".
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(npm:*, npx:*)
---

# Next.js App Router Development

Build modern Next.js applications with App Router patterns.

## File Conventions

| File | Purpose |
|------|---------|
| `page.tsx` | Route UI |
| `layout.tsx` | Shared layout |
| `loading.tsx` | Loading UI |
| `error.tsx` | Error boundary |
| `not-found.tsx` | 404 page |
| `route.ts` | API endpoint |

## Server vs Client

```tsx
// Server Component (default)
async function ServerComponent() {
  const data = await fetchData(); // Direct DB/API access
  return <div>{data}</div>;
}

// Client Component
'use client';
function ClientComponent() {
  const [state, setState] = useState(); // Hooks allowed
  return <button onClick={() => {}}>Click</button>;
}
```

## Data Fetching

```tsx
// In Server Components - direct fetch
async function Page() {
  const data = await fetch('https://api.example.com/data', {
    cache: 'force-cache', // or 'no-store'
    next: { revalidate: 3600 } // ISR
  });
  return <Component data={data} />;
}
```

## Server Actions

```tsx
// actions.ts
'use server';

export async function createItem(formData: FormData) {
  const name = formData.get('name');
  await db.insert({ name });
  revalidatePath('/items');
}
```

## Before Making Changes

1. Check `next.config.js` for project configuration
2. Review `app/` structure for routing patterns
3. Look at existing components for project conventions
```

---

## Key Takeaways

1. **Match complexity to purpose** - Simple skills need simple docs
2. **Lead with the workflow** - Show what happens step-by-step
3. **Include real code** - Concrete examples over abstract descriptions
4. **Progressive disclosure** - Main file links to details
5. **Tool restrictions** - Only allow what's needed
