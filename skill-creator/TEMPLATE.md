# Skill Templates

Copy-paste templates for creating Claude Code skills.

---

## 1. Minimal Skill

The simplest possible skill:

```yaml
---
name: my-skill
description: Brief description of what this skill does. Use when [trigger scenario].
---

# My Skill

## Instructions

[Your instructions here]
```

---

## 2. Standard Single-File Skill

A complete single-file skill with all recommended sections:

```yaml
---
name: my-skill-name
description: [Action verb] [what it does] for [domain]. Use when [scenarios]. Triggers: "[keyword1]", "[keyword2]", "[keyword3]".
allowed-tools: Read, Write, Edit, Grep, Glob
---

# My Skill Name

[One-line description of the skill's purpose]

---

## Quick Start

[Minimal steps to use this skill]

1. Step one
2. Step two
3. Step three

---

## When to Use This Skill

**Use this skill when:**
- [Scenario 1]
- [Scenario 2]
- [Scenario 3]

**Do NOT use for:**
- [Anti-pattern 1]
- [Anti-pattern 2]

---

## Instructions

### [Section 1]

[Detailed guidance]

### [Section 2]

[Detailed guidance]

---

## Examples

### Example 1: [Description]

[Code or example content]

### Example 2: [Description]

[Code or example content]

---

## Best Practices

- [Practice 1]
- [Practice 2]
- [Practice 3]

---

## Common Mistakes

1. [Mistake 1] - [How to avoid]
2. [Mistake 2] - [How to avoid]
```

---

## 3. Multi-File Skill with Progressive Disclosure

For complex skills that would exceed 500 lines:

### Directory Structure

```
my-complex-skill/
├── SKILL.md          # Main file (under 500 lines)
├── reference.md      # Detailed reference docs
├── examples.md       # Complete examples
├── patterns.md       # Common patterns
└── scripts/
    └── helper.py     # Utility scripts
```

### SKILL.md (Hub File)

```yaml
---
name: my-complex-skill
description: [Comprehensive description with action verbs]. Use when [scenarios]. Triggers: "[keyword1]", "[keyword2]".
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(python:*)
---

# My Complex Skill

[Brief overview]

---

## Quick Navigation

| Topic | File | Description |
|-------|------|-------------|
| Reference | [reference.md](reference.md) | Detailed API/syntax reference |
| Examples | [examples.md](examples.md) | Complete working examples |
| Patterns | [patterns.md](patterns.md) | Common patterns and templates |

---

## Quick Start

[Essential steps - keep this concise]

---

## Critical Rules (Quick Reference)

| Rule | Details |
|------|---------|
| [Rule 1] | [Brief explanation] |
| [Rule 2] | [Brief explanation] |
| [Rule 3] | [Brief explanation] |

---

## When to Use This Skill

**Use this skill when:**
- [Scenario 1]
- [Scenario 2]

**Do NOT use for:**
- [Anti-pattern 1]

---

## Additional Resources

For detailed documentation, see the linked files above.

## Utility Scripts

To run the helper script:
\`\`\`bash
python scripts/helper.py [args]
\`\`\`
```

---

## 4. Read-Only Skill

For skills that should only read, not modify:

```yaml
---
name: code-analyzer
description: Analyze code for patterns, bugs, and improvements. Use when reviewing code or understanding a codebase. Triggers: "analyze", "review code", "find bugs".
allowed-tools: Read, Grep, Glob
---

# Code Analyzer

Analyze code without making modifications.

---

## What This Skill Does

- Finds patterns in code
- Identifies potential bugs
- Suggests improvements (but doesn't apply them)

---

## Instructions

1. Read the target files using Read tool
2. Search for patterns using Grep
3. Report findings with recommendations

**Important**: This skill is read-only. It will NOT modify any files.

---

## Analysis Categories

### Bug Detection
- Null pointer risks
- Resource leaks
- Race conditions

### Code Quality
- Naming conventions
- Function complexity
- Duplication
```

---

## 5. Code Generation Skill

For skills that generate code in a specific language/framework:

```yaml
---
name: react-component-generator
description: Generate React components following best practices. Use when creating new React components, hooks, or pages. Triggers: "create component", "React component", "new hook".
allowed-tools: Read, Write, Edit, Grep, Glob
---

# React Component Generator

Generate React components following project conventions.

---

## Quick Start

1. Specify the component type (functional, class, hook)
2. Provide the component name
3. Describe the desired functionality

---

## Component Templates

### Functional Component

\`\`\`tsx
import React from 'react';

interface [Name]Props {
  // props
}

export const [Name]: React.FC<[Name]Props> = ({ }) => {
  return (
    <div>
      {/* content */}
    </div>
  );
};
\`\`\`

### Custom Hook

\`\`\`tsx
import { useState, useEffect } from 'react';

export const use[Name] = () => {
  const [state, setState] = useState();
  
  useEffect(() => {
    // effect
  }, []);
  
  return { state };
};
\`\`\`

---

## Conventions

- Use TypeScript for all components
- Define prop interfaces
- Use named exports
- Include JSDoc comments for complex logic

---

## When to Use

**Use this skill when:**
- Creating new React components
- Generating hooks
- Scaffolding pages

**Do NOT use for:**
- Non-React code
- Backend code
- Refactoring existing components
```

---

## 6. Workflow Automation Skill

For skills that automate multi-step workflows:

```yaml
---
name: release-manager
description: Automate release workflows including versioning, changelog, and tagging. Use when preparing a release or publishing a new version. Triggers: "release", "publish version", "create changelog".
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(git:*, npm:*)
---

# Release Manager

Automate the release process.

---

## Workflow Steps

1. **Version Bump** - Update version in package.json
2. **Changelog** - Generate changelog from commits
3. **Tag** - Create git tag
4. **Push** - Push tag to remote

---

## Commands

### Prepare Release

\`\`\`bash
# Bump version
npm version [major|minor|patch]

# Generate changelog
git log --oneline v[prev]..HEAD

# Create tag
git tag -a v[version] -m "Release v[version]"
\`\`\`

### Publish

\`\`\`bash
git push origin main --tags
\`\`\`

---

## Changelog Format

\`\`\`markdown
## [version] - YYYY-MM-DD

### Added
- New feature

### Changed
- Updated behavior

### Fixed
- Bug fix
\`\`\`
```

---

## Tips for Customizing Templates

1. **Start with the closest template** - Don't start from scratch
2. **Focus on the description first** - Get semantic matching right
3. **Add sections as needed** - Don't include empty sections
4. **Keep examples concrete** - Real code is better than placeholders
5. **Test with trigger phrases** - Verify the skill activates correctly
