---
name: tech-writer
description: >-
  Documents projects according to industry-specific writing standards with readability
  scoring and multi-format output via pandoc. Analyzes codebases, selects the right
  documentation framework (Diataxis, DITA, IEEE, APA, AMA, etc.), applies grade-level
  readability targets, and converts markdown to HTML, PDF, DOCX, or EPUB optimized for
  any display target (web, print, mobile, tablet). Use this skill whenever someone asks
  to document a project, write technical docs, create a README, write a user guide,
  generate API docs, create a spec, write a whitepaper, produce compliance documentation,
  write a report, or convert documentation between formats. Also use when the user mentions
  "plain language", "readability", "grade level", "tech writing", "documentation standards",
  "style guide", "WCAG", "accessibility", "pandoc", or asks "how should I document this".
  Even if the user just says "write docs for this" or "document this codebase" --- this skill
  applies.
---

## Overview

This skill produces documentation that meets the writing standards of the target industry, formatted for the intended audience and display device. It includes readability scoring and deterministic format conversion.

## Documentation Workflow

### Step 1: Analyze the Project

- Scan codebase structure, existing docs, README, code comments, package.json/pyproject.toml/go.mod/Cargo.toml
- Identify what exists vs what's missing
- Note the project's primary language, framework, and domain

### Step 2: Detect Document Type

Route to the appropriate workflow based on what the user is asking for:

- **README fast path** if: user asked for a README, output is `README.md`, user said "document this project" with no format/framework/industry specified, or any ambiguous single-project documentation request
- **Full pipeline (Step 3+)** if: user requested a specific output format (PDF, DOCX, HTML), a specific framework (Diataxis, DITA), a specific industry, or a non-README document type (user guide, API docs, whitepaper, compliance doc, report)

If README fast path -> proceed to the README Fast Path section below, then stop.
If full pipeline -> proceed to Step 3.

---

### README Fast Path

Use this path for all README generation. Skip the full pipeline entirely --- no industry detection, no readability scoring, no pandoc conversion. READMEs are markdown-native and stay as `.md`.

#### R1: Classify Project Type

Based on Step 1's codebase scan, classify the project:

| Type | Signals | README Emphasis |
|------|---------|----------------|
| Library/Package | Exports, registry metadata (package.json, pyproject.toml, Cargo.toml) | Installation, API surface, usage examples |
| CLI Tool | Binary entry point, argument parsing (argparse, cobra, clap), no library exports | Installation, command reference, flags/options, examples |
| Application | Server, UI, docker-compose, deployment config | Prerequisites, setup/running, configuration, env vars, deployment |
| Monorepo | Multiple packages in subdirectories, workspace config (pnpm-workspace, Cargo workspace, go.work) | Project overview, package listing with descriptions, links to sub-READMEs, shared setup |

#### R2: Detect Existing README

- If a README already exists: read it fully, identify which sections are present/missing/stale, preserve any custom content (badges, sponsors, acknowledgments, custom sections), and update rather than rewrite
- If no README exists: generate from scratch

#### R3: Select Sections

Include each section only if the project warrants it:

| Section | Include When | Skip When |
|---------|-------------|-----------|
| Title + Description | Always | Never |
| Badges | CI config exists (.github/workflows, .gitlab-ci.yml) or registry metadata | No CI, no registry |
| Features / Highlights | Always (brief for small projects) | Never |
| Prerequisites | Runtime deps, system requirements, or minimum versions | Self-contained single-file scripts |
| Installation | Always | Never |
| Usage / Quick Start | Always --- use real code examples from the codebase | Never |
| Configuration | Config files, env vars, or CLI flags exist | No configuration surface |
| API Reference | Library with public exports | CLI tool, app with no library surface |
| CLI Reference | CLI tool with commands/flags | Library, application |
| Project Structure | Monorepo, or non-obvious directory layout | Small single-purpose project with obvious layout |
| Contributing | CONTRIBUTING.md exists, or collaboration signals (PR templates, issue templates, CoC) | Personal/private projects |
| License | LICENSE file exists | No license file |

#### R4: Write the README

- Use ATX-style headings (`##` for top-level sections)
- Code examples use fenced blocks with language identifiers
- Keep descriptions concise --- READMEs are scanned, not read cover-to-cover
- Match the project's own code style conventions in examples
- No readability scoring. No pandoc conversion. Output is `README.md` directly.
- **Done. Do not proceed to Steps 3--9.**

---

### Step 3: Determine Industry Context

Use heuristics to auto-detect:
- Medical keywords (HIPAA, HL7, FHIR, FDA, clinical, patient) -> medical
- Financial keywords (SEC, FINRA, portfolio, trading, compliance) -> financial
- Government (.gov domains, federal, agency, Plain Writing Act) -> gov
- Legal (contract, statute, regulation, counsel) -> legal
- IEEE references, CAD, simulation, embedded -> engineering
- Research, citations, hypothesis, methodology -> academic
- Default -> tech

If ambiguous, ask: "This project touches [X]. Who is the primary audience for this documentation --- developers, end users, regulators, or executives?"

### Step 4: Determine Audience

Infer from context:
- API code, SDK, library -> developer
- CLI tool, desktop app, SaaS -> end-user
- Board deck, strategy doc -> executive
- Compliance, audit trail -> regulatory
- If unclear, ask one question about the audience

### Step 5: Select Documentation Framework

Decision table:

| Industry | Framework | Structure |
|----------|-----------|-----------|
| tech | Diataxis | Tutorials, How-to Guides, Reference, Explanation |
| medical | AMA + DITA topics | Conceptual, Procedural, Reference topics |
| legal | Bluebook + plain language | Numbered paragraphs, citations, plain English |
| financial | SEC plain English | Short sentences, active voice, tabular data |
| gov | Federal Plain Language | "You" voice, short sections, meaningful headings |
| engineering | IEEE 26514 | Requirements, design, test, user documentation |
| academic | APA/Chicago | Abstract, introduction, methods, results, discussion |

For details on any industry, read `references/industries.md`.

### Step 6: Apply Readability Targets

Grade level targets by industry + audience:

| Industry | Audience | Target Grade |
|----------|----------|-------------|
| medical | end-user | 4-6 |
| medical | regulatory | 8-10 |
| tech | developer | 10-14 |
| tech | end-user | 6-8 |
| financial | general | 6-8 |
| gov | general | 6-8 |
| legal | general | 8-10 |
| engineering | developer | 10-14 |
| academic | --- | 12-16 |

For readability formulas and improvement strategies, see `references/readability.md`.

### Step 7: Write Documentation in Markdown

- Use the selected framework's structure
- Apply the style guide for the industry (see `references/style-guides.md`)
- Follow audience formatting rules (see `references/audiences.md`)
- Check accessibility requirements (see `references/accessibility.md`)
- Use plain language appropriate to the grade level target

### Step 8: Check Readability

Run the readability scorer:
```bash
python3 scripts/readability.py DOCUMENT.md \
  --industry INDUSTRY --audience AUDIENCE
```
Review scores. If any metric fails, revise the document using the recommendations provided.

### Step 9: Convert to Target Format

Run the deterministic converter:
```bash
bash scripts/convert.sh \
  --input DOCUMENT.md \
  --output OUTPUT_FILE \
  --target TARGET \
  --industry INDUSTRY \
  --audience AUDIENCE \
  [--toc] [--numbered] [--paper-size letter|a4]
```

## Output Target Guide

| Target | Use When | Output Format |
|--------|----------|---------------|
| web | Documentation site, browser viewing | HTML5 with responsive CSS |
| print | Physical printing, formal distribution | PDF via xelatex, print-optimized |
| pdf-screen | On-screen PDF reading, email attachment | PDF with colored links, tighter margins |
| mobile | Phone viewing | HTML5 with mobile-first CSS |
| tablet | iPad/tablet viewing | HTML5 with responsive CSS |

## Supported Output Formats

The `--output` file extension determines the format:
- `.html` -> HTML5
- `.pdf` -> PDF (via xelatex)
- `.docx` -> Microsoft Word
- `.epub` -> EPUB ebook
- `.odt` -> OpenDocument

## Supporting Files

| File | Purpose | Load When |
|------|---------|-----------|
| `references/industries.md` | Deep industry standards reference | Working in a specific regulated industry |
| `references/readability.md` | Readability formulas and improvement strategies | Document fails readability check |
| `references/audiences.md` | Audience-specific formatting rules | Formatting for a specific audience type |
| `references/accessibility.md` | WCAG 2.1 AA / Section 508 checklist | Any web or PDF output, regulated industries |
| `references/style-guides.md` | Cross-guide quick reference for common decisions | Any writing task |

## Quick Start Examples

Example 1 --- Generate a README for a project:
Just run the skill. Document type detection routes to the README fast path automatically.
No readability scoring or format conversion needed --- output is `README.md` directly.

Example 2 --- Document a Python library for developers:
```bash
# Check readability
python3 scripts/readability.py docs/api-reference.md --industry tech --audience developer

# Convert to web
bash scripts/convert.sh --input docs/api-reference.md --output docs/api-reference.html \
  --target web --industry tech --audience developer --toc
```

Example 3 --- Patient-facing medical documentation:
```bash
# Check readability (targets grade 4-6)
python3 scripts/readability.py patient-guide.md --industry medical --audience end-user

# Convert to print PDF
bash scripts/convert.sh --input patient-guide.md --output patient-guide.pdf \
  --target print --industry medical --audience end-user --toc --paper-size letter
```

Example 4 --- Government compliance document for mobile:
```bash
python3 scripts/readability.py compliance.md --industry gov --audience general
bash scripts/convert.sh --input compliance.md --output compliance.html \
  --target mobile --industry gov --audience general --numbered
```

## Dependency Check

Before first use, verify dependencies:
```bash
bash scripts/setup-check.sh
```
