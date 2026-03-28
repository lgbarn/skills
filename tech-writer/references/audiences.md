# Audience Reference

Format, structure, voice, and conventions for each major documentation audience type.

---

## Executive / C-Suite

### Format

- **Length**: 1–3 pages maximum. 2 pages is optimal for most topics.
- **Summary placement**: Executive summary in the first paragraph. Never bury the conclusion.
- **Lists over paragraphs**: Bullet points and short sections scan faster than dense prose.
- **Visuals over tables**: Charts, graphs, and infographics communicate numbers faster than tables.
- **Financial impact**: Quantify whenever possible. Dollar figures, percentages, and time savings matter.

### Structure

1. **Executive Summary** (2–3 sentences): State what was done, why it matters, and the impact.
2. **Key Findings** (3–5 bullets): The most important facts or conclusions. No elaboration.
3. **Recommendation** (1–2 bullets): A clear action with an owner and timeline.
4. **Supporting Data** (brief, visual): Charts or a concise table. Move full data to an appendix.

### Voice

- **Solution-first**: Lead with the answer or recommendation. Save the reasoning for below.
- **Confident, decisive**: Avoid "it might be worth considering." Commit to a recommendation.
- **Jargon-free**: Define any technical term the first time it appears, or replace it.
- **Outcome-focused**: Talk about results, not process. "Reduced latency by 40%" not "refactored the caching layer."

### What to Avoid

- Code snippets or implementation details
- Lengthy methodology or background sections
- Multiple competing recommendations with no clear priority
- Ambiguous next steps ("further investigation may be needed")
- Footnotes and endnotes

---

## Developer

### Format

- **Code examples**: Include in every major section. Readers expect to copy and run them.
- **API reference**: Complete endpoint documentation. No partial coverage.
- **Runnable examples**: Copy-paste ready. Include all necessary imports and setup.
- **Version callouts**: Mark version-specific behavior clearly. Flag deprecated features with the version they were deprecated in and the replacement.

### API Reference Structure (per endpoint)

1. **Description**: 1–2 sentences. What does this endpoint do?
2. **HTTP method and URL**: `GET /api/v1/users/{id}`
3. **Parameters table**: Name | Type | Required | Description for each parameter.
4. **Request example**: Complete example with headers, authentication, and body.
5. **Response examples**: One success response (2xx), one or more error responses (4xx, 5xx).
6. **Error codes table**: Code | Meaning | How to resolve.

### Code Example Requirements

- Provide examples in multiple languages where the API or SDK supports them.
- Include all necessary imports and dependency declarations.
- Show error handling — do not show only the happy path.
- Comment lines that are non-obvious, but do not over-comment.
- Test every example with actual execution before publishing. Do not publish untested code.

### Voice

- Direct and precise. Get to the point.
- Assume technical competence. Do not explain standard programming concepts unless the audience is explicitly beginners.
- Use standard terminology consistently. Do not alternate between "endpoint," "route," and "path" for the same concept.
- Link generously to related documentation, source code, and changelogs.

### Changelog and Deprecation Notices

- Mark deprecated items with the version number and sunset date.
- Provide the migration path alongside every deprecation notice.
- Format: `**Deprecated in v2.3** — Use `newMethod()` instead. Will be removed in v3.0.`

---

## End User

### Format

- **Task-oriented structure**: Organize by what the user wants to accomplish, not by feature or product area.
- **Numbered steps**: Use numbered lists for all multi-step procedures.
- **Screenshots**: Include for any multi-step flow with a UI. Update when the UI changes.
- **FAQ section**: Address the most common questions and errors at the end.
- **Troubleshooting table**: Symptom | Likely Cause | Fix — for the most common failure modes.

### Heading Style

Write headings as task phrases (verb + noun), not as topic labels.

| Task Heading (correct) | Topic Heading (avoid) |
|------------------------|----------------------|
| Create a new project | Project Creation |
| Export your data | Data Export Procedures |
| Fix login problems | Authentication Troubleshooting |
| Connect your account | Account Connection |
| Set up notifications | Notification Settings |

### Instructions Format

1. Each step is one action. Do not combine two actions in one step.
2. Start every step with a verb: "Click", "Select", "Enter", "Open", "Toggle."
3. Bold UI element names: "Click **Save**", "Select **Settings** > **Account**."
4. Tell the user what they should see after completing the step: "The confirmation dialog appears."
5. For branching steps, use indented sub-steps or a conditional callout.

**Example:**
> 1. Click **File** in the top menu.
> 2. Select **Export**.
> 3. Choose a file format from the **Format** dropdown. The options depend on your plan.
> 4. Click **Export**. A progress bar appears. The file downloads when complete.

### Screenshot Guidelines

- **Width**: 600–800px. Wide enough to show context; narrow enough for most layouts.
- **Format**: PNG. Use lossless compression.
- **Annotation**: Add arrows, circles, or numbered callouts to highlight key UI elements.
- **Coverage**: Capture 2–4 key frames for multi-step flows. Do not screenshot every step.
- **Maintenance**: Replace screenshots immediately when the UI changes. Outdated screenshots destroy trust.

### Voice

- Friendly and encouraging. The user may be new or frustrated — be helpful, not clinical.
- Second person ("you") throughout.
- Present tense: "The dashboard shows" not "The dashboard will show."
- Short sentences. Target 15 words average. Maximum 25 words per sentence.

---

## Regulatory / Compliance

### Format

- **Version control metadata**: Every page or document header must include: document ID, version number, effective date, author, and approver.
- **Revision history table**: Append to every document. Columns: Version | Date | Author | Description of Changes | Approver.
- **Document control number**: Unique identifier used for all cross-references.
- **Controlled vocabulary**: Define all terms in a Definitions section and use them consistently. Do not paraphrase defined terms.

### Structure

1. **Document Control Block**: Document ID, title, version, effective date, author, approver, classification.
2. **Purpose and Scope**: What this document governs and what is explicitly out of scope.
3. **Definitions and Abbreviations**: All terms with specific meanings in this document.
4. **Requirements**: Numbered, traceable statements. Each requirement gets a unique ID.
5. **Compliance Evidence**: How conformance is demonstrated (audit records, test logs, certifications).
6. **Revision History**: Complete table of all versions.

### Traceability Requirements

- Each requirement is assigned a unique identifier: `REQ-SEC-001`, `REQ-PRIV-003`.
- Requirements trace forward to implementation evidence and test results.
- Requirements trace backward to their regulatory source (e.g., GDPR Article 32, ISO 27001 Annex A.12.1).
- All changes require a formal change record: request, impact analysis, approval, implementation, and verification.
- Cross-references between documents use document control numbers, not document titles (titles change; control numbers do not).

### Voice

- **Formal and precise**: Eliminate any ambiguity. Every statement must have exactly one interpretation.
- **Modal verb usage**:
  - "Shall" — mandatory requirement (avoid; prefer "must")
  - "Must" — mandatory requirement (preferred)
  - "Should" — strong recommendation
  - "May" — optional or permitted
- **Passive voice**: Acceptable in regulatory writing when the actor is the organization generally, not a specific person. "Records must be retained for 7 years."
- **No contractions**: Never use contractions in regulatory or compliance documents.
- **No ambiguous pronouns**: Spell out the subject. "The data processor must..." not "It must..."

---

## General / Mixed Audience

### Format

- **Progressive disclosure**: Structure content in layers — overview first, then details, then reference. Readers can stop when they have enough.
- **Glossary**: Required for any document that uses technical or domain-specific terms.
- **Callout boxes**: Use sidebar callouts (Note, Tip, Warning, Caution) to highlight information that does not fit inline.

**Callout types and usage:**

| Type | Use for | Visual indicator |
|------|---------|-----------------|
| Note | Additional context, clarification | Blue |
| Tip | Optional shortcut or best practice | Green |
| Warning | Potential data loss or errors | Yellow |
| Caution / Danger | Irreversible actions, safety risk | Red |

### Structure

1. **Overview**: What is this and why does it matter? One paragraph maximum.
2. **Getting Started**: The fastest path to a working result. Skip advanced options.
3. **Core Concepts**: Background knowledge needed to understand the rest. Keep brief.
4. **Detailed Sections**: Organized by topic, task, or component. The bulk of the document.
5. **Glossary**: Alphabetical list of all defined terms.
6. **Index**: For documents over 20 pages. Alphabetical entry → page or section reference.

### Voice

- **Clear and professional**: Not overly casual, not stiff.
- **Define on first use**: Write out the full term first, then abbreviate: "Transport Layer Security (TLS)".
- **Pronoun mixing**: Use second person ("you") for instructions. Use third person for conceptual descriptions ("The system processes the request").
- **Sentence length**: Target 20 words average. Vary length to maintain rhythm.
- **Headings**: Descriptive and specific. "How authentication works" not "Overview." "Configure rate limiting" not "Configuration."

### Localization Considerations

If the document may be translated or used by non-native English readers:

- Avoid idioms: "hit the ground running," "ballpark figure," "boil the ocean."
- Avoid cultural references that do not translate.
- Use simple sentence structures. Embed clauses increase translation difficulty.
- Use consistent terminology. Do not vary terms for stylistic reasons.
- Date formats: Use ISO 8601 (YYYY-MM-DD) or spell out the month: "March 21, 2026."
- Numbers: Use a comma for thousands separator and a period for decimal in US English. Note this differs in many regions.
