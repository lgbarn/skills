---
name: skill-creator
description: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Claude's capabilities with specialized knowledge, workflows, or tool integrations.
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Skill Creator

Create effective Claude Code skills following Anthropic's best practices.

---

## Quick Start

Create a minimal skill in 3 steps:

### 1. Create the directory

```bash
mkdir -p ~/.claude/skills/my-skill-name
# Or for project-specific: mkdir -p .claude/skills/my-skill-name
```

### 2. Create SKILL.md

```yaml
---
name: my-skill-name
description: [Action verb] [what it does]. Use when [scenarios]. Triggers: "[keyword1]", "[keyword2]".
---

# My Skill Name

## Instructions

[Clear, step-by-step guidance for Claude]

## Examples

[Concrete usage examples]
```

### 3. Test the skill

Ask Claude: "What skills are available?" to verify it loads, then test with your trigger phrases.

---

## Frontmatter Reference

The SKILL.md file must start with YAML frontmatter between `---` markers:

| Field | Required | Constraints | Description |
|-------|----------|-------------|-------------|
| `name` | Yes | lowercase, hyphens only, max 64 chars | Skill identifier (should match directory name) |
| `description` | Yes | max 1024 chars | What it does + when to use (Claude uses this for matching) |
| `allowed-tools` | No | comma-separated | Restrict tool access for security |
| `model` | No | full model name | Override conversation model |

### allowed-tools Examples

```yaml
# Read-only skill
allowed-tools: Read, Grep, Glob

# File editing skill
allowed-tools: Read, Write, Edit, Grep, Glob

# Bash with specific commands
allowed-tools: Read, Bash(git:*, npm:*, docker:*)

# Full access (omit field entirely)
# (no allowed-tools field)
```

---

## Writing Effective Descriptions

Claude matches user requests against skill descriptions using semantic similarity. A good description is critical for proper skill activation.

### The Description Formula

```
[Action verb(s)] + [what it does] + [target domain].
Use when [specific trigger scenarios].
Triggers: "[keyword1]", "[keyword2]", "[keyword3]".
```

### Good vs Bad Descriptions

**Good** (specific, action-oriented, includes triggers):
```yaml
description: Create, modify, debug, and convert trading indicators for TradingView and NinjaTrader. Use when writing new indicators, adding features, or converting between platforms. Triggers: "create indicator", "Pine Script", "NinjaScript".
```

**Bad** (vague, no triggers):
```yaml
description: Helps with trading stuff.
```

### Description Checklist

- [ ] Starts with action verbs (create, configure, debug, analyze, generate)
- [ ] Explains what the skill does
- [ ] Specifies the domain/context
- [ ] Includes "Use when..." guidance
- [ ] Lists trigger keywords users would naturally say
- [ ] Under 1024 characters

---

## File Organization

### Single-File Skills

For simple skills under 500 lines:

```
my-skill/
└── SKILL.md
```

### Multi-File Skills (Progressive Disclosure)

For complex skills, split content to keep SKILL.md under 500 lines:

```
my-skill/
├── SKILL.md          # Essential info + links (under 500 lines)
├── reference.md      # Detailed documentation
├── examples.md       # Usage examples
└── scripts/
    └── helper.py     # Utility scripts (executed, not loaded)
```

**Why progressive disclosure?**
- Only SKILL.md loads initially
- Claude reads supporting files only when needed
- Keeps context focused and efficient
- Allows bundling comprehensive documentation

### Linking Supporting Files

In SKILL.md, link to supporting files:

```markdown
## Additional Resources

- For complete API details, see [reference.md](reference.md)
- For usage examples, see [examples.md](examples.md)

## Utility Scripts

To validate input, run:
\`\`\`bash
python scripts/helper.py input.txt
\`\`\`
```

---

## Skill Locations

| Location | Path | Scope | Use Case |
|----------|------|-------|----------|
| Personal | `~/.claude/skills/` | All your projects | General-purpose skills |
| Project | `.claude/skills/` | This repository only | Project-specific skills |
| Plugin | `skills/` in plugin dir | Anyone with plugin | Distributed skills |

**Precedence**: Enterprise > Personal > Project > Plugin

---

## Common Mistakes

### 1. Vague Description

```yaml
# Bad
description: Helps with documents

# Good
description: Extract text, fill forms, and merge PDF files. Use when working with PDFs or document extraction. Triggers: "PDF", "fill form", "merge documents".
```

### 2. SKILL.md Too Long

If over 500 lines, split into supporting files. Claude's context is shared with conversation history.

### 3. Missing Trigger Keywords

Include words users naturally say:
- "create", "make", "build", "generate"
- "fix", "debug", "troubleshoot"
- "convert", "transform", "migrate"
- Domain-specific terms

### 4. Overly Broad allowed-tools

```yaml
# Bad - too permissive
allowed-tools: Read, Write, Edit, Bash, WebFetch, WebSearch

# Good - only what's needed
allowed-tools: Read, Grep, Glob
```

### 5. Hardcoded Absolute Paths

```markdown
# Bad
See /Users/john/projects/docs/reference.md

# Good
See [reference.md](reference.md)
```

### 6. No "When to Use" Guidance

Always include a section explaining when to use (and not use) the skill.

---

## When to Use This Skill

**Use this skill when:**
- Creating a new skill from scratch
- Updating an existing skill
- Learning skill best practices
- Debugging why a skill isn't triggering

**Do NOT use for:**
- General coding tasks
- Tasks unrelated to skill creation

---

## Skill Templates

For copy-paste templates, see [TEMPLATE.md](TEMPLATE.md).

## Complete Examples

For full working examples, see [EXAMPLES.md](EXAMPLES.md).

## Pre-Flight Checklist

Before finalizing a skill, see [CHECKLIST.md](CHECKLIST.md).

---

## Workflow for Creating a New Skill

1. **Define the purpose** - What problem does this skill solve?
2. **Choose location** - Personal (`~/.claude/skills/`) or project (`.claude/skills/`)?
3. **Write description first** - Get the semantic matching right
4. **Draft SKILL.md** - Start with template, customize
5. **Add supporting files** - If needed for progressive disclosure
6. **Test activation** - Verify skill triggers on expected phrases
7. **Iterate** - Refine based on real usage

---

## Testing Skills

### Verify Skill Loads

Ask Claude: "What skills are available?"

### Test Trigger Phrases

Try phrases from your description's trigger keywords:
- "Help me [trigger keyword]"
- "I need to [action verb from description]"
- "[Domain term] assistance"

### Debug Non-Triggering Skills

If skill doesn't activate:
1. Check SKILL.md syntax (valid YAML, no tabs)
2. Verify description includes semantic keywords
3. Ensure no blank lines before opening `---`
4. Run `claude --debug` for error messages
