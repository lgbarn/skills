# Skill Validation Checklist

Pre-flight checklist before deploying a Claude Code skill.

---

## Required Checks

### Frontmatter

- [ ] SKILL.md starts with `---` on first line
- [ ] Frontmatter ends with `---` on its own line
- [ ] `name` field is present and lowercase with hyphens
- [ ] `name` matches the directory name
- [ ] `description` field is present
- [ ] `description` is under 1024 characters

### Description Quality

- [ ] Starts with action verb (Create, Generate, Review, etc.)
- [ ] Explains WHAT the skill does
- [ ] Explains WHEN to use it
- [ ] Includes `Triggers:` with 3-5 keywords
- [ ] Keywords match how users naturally phrase requests

### File Size

- [ ] SKILL.md is under 500 lines
- [ ] If over 500 lines, content is split into linked files
- [ ] Supporting files are referenced from SKILL.md

### Security (if applicable)

- [ ] `allowed-tools` restricts to necessary tools only
- [ ] Bash commands are scoped (e.g., `Bash(git:*, npm:*)`)
- [ ] No overly broad permissions like `Bash(*)` unless required

---

## Recommended Checks

### Content Quality

- [ ] Includes Quick Start or Workflow section
- [ ] Has concrete code examples
- [ ] Avoids vague language ("helps with", "assists in")
- [ ] Uses tables for reference information
- [ ] Includes "When to Use" guidance

### Portability

- [ ] No hardcoded absolute paths
- [ ] Uses relative paths or `{baseDir}` placeholder
- [ ] Works across different project structures

### Organization

- [ ] Sections use clear headers
- [ ] Complex content uses tables
- [ ] Code examples have syntax highlighting
- [ ] Links to supporting files work

---

## Quick Validation Commands

```bash
# Check frontmatter syntax
head -20 SKILL.md

# Count lines
wc -l SKILL.md

# Check description length
sed -n '/^description:/p' SKILL.md | wc -c

# List linked files
grep -oE '\[.*\]\(.*\.md\)' SKILL.md
```

---

## Common Issues

| Issue | Fix |
|-------|-----|
| Skill not triggering | Add more trigger keywords to description |
| Description too long | Move details to body, keep description concise |
| Wrong tools available | Check `allowed-tools` spelling and syntax |
| Linked file not found | Verify relative path is correct |
| Skill loads slowly | Split large files, use progressive disclosure |

---

## Test Your Skill

After creating the skill:

1. **Trigger test**: Ask Claude using your trigger keywords
2. **Tool test**: Verify only expected tools are available
3. **Content test**: Check that guidance is clear and actionable
4. **Edge cases**: Test with variations of trigger phrases

Example test prompts:
```
"[trigger keyword 1]"
"help me [trigger keyword 2]"
"I need to [trigger keyword 3]"
```
