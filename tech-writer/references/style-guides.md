# Style Guide Cross-Reference

Common style decisions and how major guides handle them. Use this when a client has not specified a house style, or when you need to reconcile conflicting guidance.

---

## Oxford / Serial Comma

The Oxford comma is the comma placed before the final conjunction in a list of three or more items ("red, white, and blue").

| Guide | Use Oxford Comma? |
|-------|-------------------|
| Google Developer | Yes |
| Microsoft | Yes |
| Apple | Yes |
| APA (7th ed.) | Yes |
| Chicago (17th ed.) | Yes |
| AP Stylebook | No |
| AMA (11th ed.) | Yes |

**Recommendation**: Always use the Oxford comma unless the client explicitly follows AP style. Omitting it occasionally creates ambiguity ("I'd like to thank my parents, God and Ayn Rand"). Using it never creates ambiguity.

---

## Numbers

When to spell out numbers versus use numerals varies by guide and context.

| Guide | Spell Out |
|-------|-----------|
| AP | Numbers under 10 |
| Chicago (humanities) | Numbers under 100 |
| Chicago (sciences) | Numbers under 10 |
| APA | Numbers under 10 |
| AMA | Numbers under 10 |
| Google / Microsoft | Context-dependent (see notes below) |

**Google and Microsoft notes**: Use numerals when the number is part of a technical context (version numbers, measurements, UI settings, counts in a table, code). Spell out when used conversationally ("three options are available"). Always use numerals for 10 and above.

**Universal exceptions** (use numerals regardless of guide):
- Numbers at the start of a sentence: rewrite to avoid, or spell out the number.
- Percentages: "5%" not "five percent" (except at the start of a sentence).
- Measurements with units: "3 GB," "15 ms," "2.4 GHz."
- Versions: "version 3," "v2.1."
- Statistics in tables.

---

## Heading Capitalization

Two systems: title case and sentence case.

**Title case**: Capitalize the first letter of all major words. Lowercase articles, short prepositions, and coordinating conjunctions unless they are the first word.
- Example: "Configure Your Authentication Settings"

**Sentence case**: Capitalize only the first word and proper nouns.
- Example: "Configure your authentication settings"

| Guide | Heading Style |
|-------|--------------|
| Google Developer | Sentence case |
| Microsoft | Sentence case |
| Apple | Title case |
| APA (levels 1–2) | Title case |
| APA (levels 3–5) | Sentence case |
| Chicago | Title case |
| Federal Plain Language | Sentence case recommended |

**Recommendation**: Default to sentence case for technical documentation. It is easier to apply consistently and reduces decisions about which words to capitalize.

---

## Abbreviations and Acronyms

**Universal rule (all guides)**: Define on first use.
- Format: spell out the term first, then put the abbreviation in parentheses.
- Example: "Transport Layer Security (TLS)"
- After the definition, use the abbreviation consistently throughout the document.

**Long documents (20+ pages)**: Re-define the abbreviation at the start of each major chapter or section. Readers may enter from a bookmark or link.

**Well-known abbreviations**: For technical audiences, widely understood abbreviations (URL, HTML, API, JSON, HTTP, SQL, DNS) may not require definition. When in doubt, define.

**Plural abbreviations**: Add a lowercase "s" with no apostrophe: "APIs," "URLs," not "API's" or "URL's."

**Avoid starting sentences with abbreviations**: Rewrite or spell out the term.

---

## Active vs Passive Voice

| Guide | Guidance |
|-------|----------|
| Google Developer | Active voice preferred |
| Microsoft | Active voice preferred |
| APA | Active voice preferred; passive acceptable in methods sections |
| AMA | Active voice preferred; passive acceptable in scientific context |
| Legal (plain language) | Active voice for plain language; passive sometimes needed for precision |
| SEC Plain English | Active voice required |
| Federal Plain Language | Active voice required |
| Regulatory / Compliance | Passive acceptable when the actor is the organization generally |

**When passive voice is acceptable:**
- Scientific methodology: "Samples were collected between March and June."
- When the actor is unknown or irrelevant: "The package was delivered."
- Regulatory writing emphasizing the action rather than who performs it: "Records must be retained for 7 years."

**When to convert to active:**
- Any time the actor is known and the information adds value.
- Any time the passive construction is longer or less clear.
- Instructional content: always use active voice ("Click Save" not "Save should be clicked").

---

## Gender-Neutral Language

All modern style guides require gender-neutral language.

**Singular "they"**: Preferred by APA, Chicago, Google, Microsoft, and Apple as the generic singular pronoun. "Each user can customize their dashboard."

**Common substitutions:**

| Gendered | Neutral |
|----------|---------|
| chairman | chairperson, chair |
| fireman | firefighter |
| policeman | police officer |
| mankind | humankind, people, humanity |
| he/she | they |
| his or her | their |
| husband/wife | spouse, partner |
| stewardess | flight attendant |
| salesman | salesperson, sales representative |

**Best practice for instructions**: Address the reader as "you." This eliminates the need for any third-person pronoun and is preferred for all user-facing documentation.

---

## Inclusive Language

**Person-first language**: "Person with a disability" not "disabled person." This is the default in most US and Canadian style guides, though identity-first language ("autistic person") is preferred by many in the autism community. When writing for a specific community, follow their stated preference.

**Ableist language to avoid:**

| Avoid | Use instead |
|-------|-------------|
| sanity check | final check, validation |
| blind spot | gap, oversight |
| crippled | limited, restricted |
| dummy | placeholder, example |
| crazy / insane | unexpected, significant |
| lame | poor, weak |

**Technology-specific inclusive terms:**

| Avoid | Use instead |
|-------|-------------|
| whitelist | allow list |
| blacklist | deny list, block list |
| master | main, primary, source |
| slave | replica, secondary, worker |
| grandfathered | legacy, exempted |

---

## Lists

**Numbered lists**: Use for sequential steps, ranked items, or any list where order matters.

**Bulleted lists**: Use for non-sequential items, features, requirements, or any list where order does not matter.

**Parallel structure**: All items in a list must be grammatically parallel.
- All start with a verb: "Install the package. Configure the settings. Restart the service."
- All are noun phrases: "Authentication, Authorization, Session management."
- Mixing forms (some verbs, some nouns) is a style error.

**Punctuation:**
- If items are complete sentences: end each with a period.
- If items are fragments: no period at the end of each item.
- Be consistent within a single list. Do not mix complete sentences and fragments.

**Introductory sentence**: Introduce lists with a complete sentence ending in a colon. Do not use a fragment, and do not put a colon after a verb or preposition.
- Correct: "The following options are available:"
- Incorrect: "The options are:" (colon after a verb)
- Incorrect: "You can choose from:" (colon after a preposition)

**Nesting**: Limit to two levels of nesting. Three or more levels signal that the content should be restructured.

---

## Technical Term Introduction

Two standard patterns for introducing technical terms:

**Pattern 1 — Plain description first, term in parentheses:**
- "The server sends back data (the response)."
- "We use a public key infrastructure (PKI) to manage certificates."

**Pattern 2 — Term first, definition in apposition or parentheses:**
- "A container orchestration platform — such as Kubernetes — manages deployment, scaling, and operations."
- "Latency (the time between a request and its response) affects user experience."

**Choose based on audience:**
- For general or mixed audiences, use Pattern 1. Readers see the plain language first.
- For technical audiences who already know the term, use Pattern 2 as reinforcement.

**After introduction**: Use the technical term consistently. Do not alternate between the term and its plain-language synonym.
