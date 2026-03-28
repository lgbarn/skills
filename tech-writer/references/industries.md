# Industry-Specific Documentation Standards

Deep reference for documentation standards, citation formats, and writing conventions by industry.

---

## Software / Technology

### Diátaxis Framework

The Diátaxis framework defines 4 documentation types. Choose type based on user need, not topic.

| Type | Orientation | User Need |
|------|-------------|-----------|
| Tutorials | Learning | Step-by-step lessons for beginners |
| How-to Guides | Problem | Practical steps to accomplish a specific goal |
| Reference | Information | Complete and accurate lookup material |
| Explanation | Understanding | Clarifying concepts, background, and context |

**Tutorials** — The user is learning. Guide them through a complete, working example. Success is measured by whether the user finishes with something functional and understands what they did.

**How-to Guides** — The user knows what they want to accomplish but not how. Provide focused, actionable steps. Do not explain why unless necessary to complete the task.

**Reference** — The user needs accurate, complete information. Structure for scanning. Consistency and completeness matter more than prose quality. API docs, CLI references, configuration keys.

**Explanation** — The user wants to understand. Discuss alternatives, trade-offs, history, and context. Not for instructions. Good for architecture docs, concept guides, design rationale.

### Google Developer Documentation Style Guide

Key rules for technical documentation:

- **Pronouns**: Use second person ("you"). Avoid "the user" or "one."
- **Voice**: Active voice. "Click Save" not "Save should be clicked."
- **Tense**: Present tense. "The function returns" not "the function will return."
- **Punctuation**: Use the serial (Oxford) comma.
- **Global audience**: Write for international readers. Avoid idioms, slang, culturally specific references, humor, and sports metaphors.
- **Headings**: Sentence-style capitalization ("Set up your environment" not "Set Up Your Environment").
- **Abbreviations**: Define on first use. "Transport Layer Security (TLS)".
- **Links**: Link to related content generously. Link text must describe the destination.
- **Code**: Use code font for all code, command names, file paths, parameters, and UI strings that require exact input.

### Microsoft Writing Style Guide

Key rules and tone:

- **Voice**: Warm, relaxed, crisp, clear. Write like a knowledgeable friend, not a formal manual.
- **Sentence structure**: Simple subject + verb + object. Avoid embedded clauses.
- **Capitalization**: Sentence case for headings and titles.
- **Contractions**: OK in most contexts. Use them to keep a conversational tone.
- **User focus**: Write about what the user can do, not what the product does. "You can set a reminder" not "The app enables reminders."
- **Accessibility**: Use inclusive language. Follow WCAG guidance for digital content.
- **Numbers**: Use numerals for 10 and above; spell out one through nine. Use numerals always for UI, versions, measurements.

### Apple Style Guide

Differences from Google/Microsoft:

- **Disability and inclusive writing**: Detailed guidance on accessibility-related terminology. Person-first and identity-first usage described per community preference.
- **Contractions**: Avoid contractions in formal documentation (help articles and user guides may differ).
- **Product names**: Capitalize precisely. "iPhone" not "Iphone" or "iphone". "macOS" not "MacOS".
- **Pronouns**: Avoid gendered pronouns. Rephrase or use "they/them."
- **UI elements**: Bold UI element names. "Tap **Settings**."

---

## Medical / Healthcare

### AMA Manual of Style (11th Edition)

Citation and manuscript format:

- **Citations**: Numbered in the order they appear in the text. Superscript numbers in the body.
- **Reference list**: Numbered order (not alphabetical). Listed at end of document.
- **Author format**: Last name + initials without periods or spaces. "Smith JA, Jones RB."
- **Journal articles**: Author(s). Title. Journal abbreviation. Year;Volume(Issue):Pages.
- **Structured abstracts**: Required for clinical research. Standard sections: Objective, Methods, Results, Conclusions.
- **Units**: SI units preferred. Express lab values in SI; provide conventional units in parentheses where relevant.
- **Statistics**: Report exact p values (p=.03) rather than p<.05. Include confidence intervals.

### FDA Plain Language Mandates

Readability requirements for patient-facing content:

- **Patient materials**: Target 3rd–5th grade reading level.
- **Nonprescription drug labels**: Target 4th–5th grade.
- **Measurement tool**: Use CDC Clear Communication Index for evaluation.
- **Jargon**: Avoid all medical jargon in patient-facing content. Define every technical term used.
- **Sentence length**: Average 15–20 words for patient materials.
- **Testing**: User test patient materials with representative members of the target population.

### SMOG Index

Primary readability metric for healthcare documentation:

- **What it measures**: Predicts 100% comprehension (unlike Flesch-Kincaid and Gunning Fog, which predict 50–75% comprehension).
- **Formula**: 1.0430 × √(polysyllables × 30/sentences) + 3.1291
- **Polysyllabic words**: Words with 3 or more syllables.
- **Designed for**: 30+ sentence samples. Shorter texts are extrapolated and less accurate.
- **Target**: Grade 6 or below for most patient-facing materials.
- **When to use SMOG**: Whenever the audience includes patients, caregivers, or the general public.

### Patient-Facing vs Clinician-Facing

| Dimension | Patient-Facing | Clinician-Facing |
|-----------|---------------|-----------------|
| Reading level | Grade 4–6 | Grade 10–14+ |
| Vocabulary | Plain language only | Technical vocabulary OK |
| Sentence length | 10–15 words average | 20–25 words acceptable |
| Voice | Active, second person | Active preferred; passive OK |
| Methodology | Omit or simplify | Include with detail |
| Citations | Avoid or use lay summaries | Full AMA-style required |
| Examples | Relatable scenarios | Clinical case examples |

---

## Legal

### Bluebook Citation Format

Standard legal citation system used in law journals and courts:

- **Cases**: Party v. Party, Volume Reporter Page (Court Year). Example: *Roe v. Wade*, 410 U.S. 113 (1973).
- **Statutes**: Title Code § Section (Year). Example: 42 U.S.C. § 1983 (2018).
- **Regulations**: Title C.F.R. § Section (Year). Example: 21 C.F.R. § 312.1 (2023).
- **Italics**: Italicize case names when cited in text. Do not italicize in footnotes.
- **Short forms**: After first full citation, use short forms (e.g., *Roe*, 410 U.S. at 120; *id.* at 121).

### ALWD Citation Format

Alternative to Bluebook, preferred in some law schools and practice settings:

- **Simpler rules**: Fewer exceptions and special cases than Bluebook.
- **Clear examples**: Each citation type illustrated with a concrete example.
- **More accessible**: Better suited for practitioners who write for courts, not law reviews.
- **Differences**: ALWD omits certain large and small caps requirements; handles spacing and abbreviations differently.

### Bryan Garner's Plain Language Principles for Legal Writing

- **Front-load the conclusion**: State the result or recommendation first, then provide support.
- **Sentence length**: Average 20 words. No sentence should exceed 60 words.
- **Word choice**: Prefer common words. "End" not "terminate." "Use" not "utilize." "Before" not "prior to."
- **Eliminate legalese**: Remove *hereinafter*, *whereas*, *pursuant to*, *notwithstanding*, *in witness whereof*.
- **Voice**: Active voice wherever possible.
- **Structure**: Use numbered lists for requirements, conditions, and elements of a test.
- **Defined terms**: Define terms of art once, bracket the definition, and use the term consistently thereafter.

### Legal Document Types and Their Conventions

**Contracts**
- Defined terms in ALL CAPS or Title Case, listed in a Definitions section
- Numbered sections and subsections
- Recitals (whereas clauses) in preamble
- Representations, warranties, covenants in separate articles
- Signature block at end

**Briefs**
- Statement of the Issue(s)
- Statement of Facts (favorable facts emphasized)
- Standard of Review
- Argument (headings as thesis statements)
- Conclusion (specific relief requested)

**Memoranda**
- Issue (the legal question)
- Brief Answer (1–2 sentences)
- Facts (relevant background)
- Discussion (analysis applying law to facts)
- Conclusion (restate recommendation)

---

## Financial

### SEC Plain English Handbook

Required for prospectuses and disclosure documents:

- **Sentences**: Short, averaging 15–20 words.
- **Voice**: Active. "We will redeem the notes" not "The notes will be redeemed."
- **Pronouns**: Use "we" and "you." Avoids the formal distance of third person.
- **Jargon**: Eliminate legal and financial jargon. Define any retained technical terms.
- **Numerical data**: Use tables for complex numbers. Do not bury figures in paragraphs.
- **Organization**: Put the most important information first (inverted pyramid).
- **What to eliminate**: Unnecessary provisions, repetition, and cross-references that force readers to jump to other pages.

### FINRA Communication Guidelines (Rule 2210)

Three categories of public communications:

| Category | Definition | Requirements |
|----------|------------|--------------|
| Correspondence | Personalized to fewer than 25 retail investors in 30 days | Post-use review |
| Retail Communication | Reaches 25+ retail investors | Principal approval before use |
| Institutional Communication | Reaches only institutional investors | Post-use review |

All communications must be:
- Fair and balanced
- Not misleading
- Based on principles of fair dealing
- Consistent with applicable rules and regulations

**Retail communication**: Requires prior principal approval. Must not exaggerate performance, omit material facts, or make promissory statements about returns.

### Annual Report vs Prospectus

| Dimension | Annual Report | Prospectus |
|-----------|--------------|------------|
| Primary audience | Shareholders, analysts, media | Prospective investors |
| Structure | Narrative-driven, flexible | SEC-mandated structure |
| Design | Heavy visual design, charts, photos | Minimal design, dense text |
| Legal requirement | Required for public companies | Required for securities offerings |
| Key sections | Letter to shareholders, MD&A, financials | Risk factors, use of proceeds, financials |
| Tone | Reflective, optimistic | Objective, risk-disclosing |

---

## Government

### Plain Writing Act of 2010

Federal agencies must use plain language in documents that:
- Explain how to obtain benefits or services
- Provide information about federal benefits or services
- Explain how to comply with a requirement that the agency administers

Does not apply to: internal documents, regulations (separately governed), or documents not addressed to the public.

### Federal Plain Language Guidelines

Core requirements for all covered documents:

- **Pronouns**: Use "you" when addressing the reader, "we" for the agency.
- **Voice**: Active. "You must file by April 15" not "The form must be filed by April 15."
- **Sentences**: Short sentences (one idea per sentence). Short paragraphs (3–5 sentences maximum).
- **Words**: Common everyday words. "Help" not "facilitate." "Use" not "utilize." "Buy" not "purchase."
- **Requirements**: Use "must" for mandatory requirements. Do not use "shall" (ambiguous).
- **Recommendations**: Use "should."
- **Structure**: Use headings, lists, and tables. Organize by user task, not by agency structure.
- **Sections**: Write short sections. Each section answers one question or covers one topic.
- **Cross-references**: Minimize. If needed, spell out the referenced section.

### Section 508 Compliance

All federal electronic information and communication technology must be accessible to people with disabilities.

- **Standard**: WCAG 2.1 Level AA (as incorporated by the Revised 508 Standards).
- **Scope**: Web content, software, electronic documents, hardware with embedded software.
- **Documents**: PDFs must be tagged and accessible. Word and PowerPoint files follow same principles.
- **Testing**: Automated tools (axe, WAVE) plus manual screen reader testing.

---

## Engineering

### IEEE 830 — Software Requirements Specification (SRS)

Standard structure for software requirements documents:

1. **Introduction**
   - Purpose (who will read the SRS and what they will do with it)
   - Scope (name of software, what it does and does not do)
   - Definitions, acronyms, abbreviations
   - References
   - Overview

2. **Overall Description**
   - Product perspective (system context, interfaces)
   - Product functions (summary of major functions)
   - User characteristics (technical level, domain knowledge)
   - Constraints (regulatory, hardware, software, interface)
   - Assumptions and dependencies

3. **Specific Requirements**
   - External interface requirements (user, hardware, software, communication)
   - Functional requirements (organized by feature or use case)
   - Performance requirements (response time, throughput, capacity)
   - Design constraints (standards compliance, hardware limitations)
   - Quality attributes (reliability, maintainability, portability)

### IEEE 829 — Test Documentation

Standard set of test documents:

| Document | Purpose |
|----------|---------|
| Test Plan | Scope, approach, resources, schedule |
| Test Design Specification | Features to be tested, test approach |
| Test Case Specification | Inputs, execution conditions, expected results |
| Test Procedure Specification | Steps to execute a test case |
| Test Item Transmittal Report | Items being delivered for testing |
| Test Log | Chronological record of test execution |
| Test Incident Report | Description of anomalous events |
| Test Summary Report | Results evaluation and recommendations |

### ISO/IEC/IEEE 26514 — User Documentation

Standard for design and development of software user documentation:

- **Audience analysis**: Required before planning begins. Document user characteristics, tasks, and environments.
- **Planning**: Documentation plan covers scope, audience, format, schedule, and resources.
- **Design**: Information architecture based on user tasks and goals.
- **Development**: Writing, illustration, and multimedia production to plan specifications.
- **Editing**: Structural, copy, and technical edit passes defined separately.
- **Testing**: Usability testing with representative users required.
- **Maintenance**: Change tracking, version control, and update procedures.

### Requirements Traceability

- Each requirement has a unique identifier (e.g., REQ-AUTH-001).
- Requirements trace forward: REQ → Design element → Test case.
- Requirements trace backward: Test case → REQ → business need.
- All changes go through formal change control: request, impact analysis, approval, implementation, verification.
- Traceability matrix maintained throughout the project lifecycle.
- Traceability gaps (untested requirements, tests without requirements) are defects.

---

## Scientific / Academic

### APA 7th Edition

Key formatting and citation rules:

- **In-text citations**: (Author, Year) for paraphrase; (Author, Year, p. X) for direct quote.
- **Multiple authors**: Two authors — (Smith & Jones, 2021). Three or more — (Smith et al., 2021).
- **Reference list**: Alphabetical by first author's last name. Hanging indent.
- **DOI**: Include as hyperlink when available. No period after DOI.
- **Running head**: Not required for student papers; required for manuscripts submitted for publication.
- **Abstract**: 150–250 words. One paragraph, no indentation.

**Heading levels:**

| Level | Format |
|-------|--------|
| 1 | Centered, bold, title case |
| 2 | Left aligned, bold, title case |
| 3 | Left aligned, bold italic, title case |
| 4 | Indented, bold, sentence case, period |
| 5 | Indented, bold italic, sentence case, period |

### Chicago Manual of Style (17th Edition)

Two documentation systems:

- **Notes-bibliography**: Used in humanities (history, literature, arts). Footnotes or endnotes + bibliography.
- **Author-date**: Used in sciences and social sciences. In-text citations + reference list.

**Notes-bibliography** — Full citation in first footnote; shortened form on subsequent references. Bibliography at end, alphabetical by author.

**Author-date** — Same structure as APA but with Chicago-specific formatting differences (no comma between author and year in text, slightly different reference list formatting).

**Preferred by**: Business writing, history, fine arts, and publishers who want comprehensive style coverage.

### Abstract Structure

Standard for scientific papers:

1. **Background/Context**: What problem or gap does the work address?
2. **Objective/Purpose**: What did you set out to do?
3. **Methods**: How did you do it? (brief)
4. **Results**: What did you find? (key findings only)
5. **Conclusions**: What does it mean? What should readers take away?

**Length**: 150–300 words for most journals. Check target journal requirements.

**Rules**:
- Standalone — must be comprehensible without reading the paper
- No citations (unless absolutely necessary)
- No abbreviations undefined in the abstract itself
- Written in past tense (for what was done) and present tense (for what the results mean)
