# Skills

Skills are folders of instructions, scripts, and resources that Claude loads dynamically to improve performance on specialized tasks. Skills teach Claude how to complete specific tasks in a repeatable way, whether that's creating documents with your company's brand guidelines, analyzing data using your organization's specific workflows, or automating personal tasks.

For more information, check out:

- [What are skills?](https://support.claude.com/en/articles/12512176-what-are-skills)
- [Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
- [How to create custom skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)
- [Equipping agents for the real world with Agent Skills](https://anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

# About This Repository

This repository contains Luther Barnum's custom skills for Claude.

**Included skills:**
- **indicator-generator** - Create TradingView Pine Script and NinjaTrader indicators/strategies
- **python-trading-bot** - Generate Python trading bots for NQ futures (Apex Trader Funding)
- **ci-cd-setup** - Configure CI/CD pipelines for trading projects
- **changelog-generator** - Create user-friendly changelogs from git commits
- **skill-creator** - Create new Claude skills
- **skill-share** - Share skills via Slack
- **ship** - Full commit, push, and CI verification workflow
- **fix-lint** - Fix lint errors and re-stage files after pre-commit hook failures
- **tech-writer** - Industry-specific documentation with readability scoring and multi-format output
- **dashpilot** - Chrome extension + MCP server for live read-only browser tab inspection
- **recipe-creator** - Original recipes grounded in culinary science, world cuisines, and flavor pairing
- **systems-design** - System design interview prep and architecture guide for DoD/Coast Guard IL2/IL4 on AWS GovCloud
- **troubleshoot** - Deep diagnosis of trading bot issues via layered diagnostic methodology

Each skill is self-contained in its own folder with a `SKILL.md` file containing the instructions and metadata that Claude uses.

# Skill Sets

- **Trading Skills**: indicator-generator, python-trading-bot, ci-cd-setup, troubleshoot
- **Development Workflow**: ship, fix-lint, changelog-generator
- **Documentation & Writing**: tech-writer, recipe-creator
- **Architecture**: systems-design
- **Tools & Meta**: skill-creator, skill-share, dashpilot

# Try in Claude Code, Claude.ai, and the API

## Claude Code

You can register this repository as a Claude Code Plugin marketplace by running the following command in Claude Code:

```
/plugin marketplace add lgbarn/skills
```

Then, to install a specific set of skills:

1. Select `Browse and install plugins`
2. Select `lgbarn-skills`
3. Select the skill set you want to install
4. Select `Install now`

After installing the plugin, you can use the skill by just mentioning it. For instance, you can ask Claude Code to do something like: "Create a Keltner Channel indicator for TradingView"

## Claude.ai

To use skills from this repository in Claude.ai, follow the instructions in [Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude#h_a4222fa77b).

# Creating a Basic Skill

Skills are simple to create - just a folder with a `SKILL.md` file containing YAML frontmatter and instructions. You can use the **template-skill** in this repository as a starting point:

```markdown
---
name: my-skill-name
description: A clear description of what this skill does and when to use it
---

# My Skill Name

[Add your instructions here that Claude will follow when this skill is active]

## Examples

- Example usage 1
- Example usage 2

## Guidelines

- Guideline 1
- Guideline 2
```

The frontmatter requires only two fields:

- `name` - A unique identifier for your skill (lowercase, hyphens for spaces)
- `description` - A complete description of what the skill does and when to use it

The markdown content below contains the instructions, examples, and guidelines that Claude will follow. For more details, see [How to create custom skills](https://support.claude.com/en/articles/12512198-creating-custom-skills).

