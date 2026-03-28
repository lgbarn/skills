# Readability Reference

Formulas, grade level interpretation, and rewriting strategies for documentation.

---

## Readability Formulas

### Flesch-Kincaid Grade Level

**Formula**: 0.39 × (words/sentences) + 11.8 × (syllables/words) − 15.59

**Interpretation**: Result is the approximate US school grade level required to understand the text on first reading.

**Example**: A score of 8.2 means a typical 8th grader should be able to understand the text.

**Best for**: General documents, business writing, technical documentation.

**Notes**:
- Sensitive to sentence length and syllable count.
- Reducing average sentence length has the greatest impact on score.
- Does not account for vocabulary difficulty beyond syllable count.

---

### Gunning Fog Index

**Formula**: 0.4 × ((words/sentences) + 100 × (complex_words/words))

**Complex words**: Words with 3 or more syllables, excluding words where the extra syllables come from -ing, -ed, or -es suffixes (e.g., "created" and "running" are not counted as complex).

**Interpretation**: Approximate years of formal education needed for first-read comprehension.

**Example**: A score of 12 requires a high school graduate's reading level.

**Best for**: Identifying documents with too many polysyllabic words.

**Notes**:
- More sensitive to vocabulary than Flesch-Kincaid.
- Useful for catching dense jargon even in short sentences.
- Scores above 17 are considered unreadable by most standards.

---

### SMOG Index

**Formula**: 1.0430 × √(polysyllables × 30/sentences) + 3.1291

**Polysyllabic words**: Words with 3 or more syllables (all such words; no suffix exclusions).

**Unique property**: SMOG predicts 100% comprehension of the text. Other formulas (Flesch-Kincaid, Gunning Fog) predict 50–75% comprehension. This makes SMOG the conservative standard — a SMOG grade 6 means essentially all target readers at that level will understand.

**Best for**: Healthcare content, patient materials, public health communications.

**Designed for**: 30+ sentence samples. Applying SMOG to fewer than 30 sentences involves extrapolation and reduces accuracy.

**Target**: Grade 6 or below for patient-facing materials. Grade 8 or below for general public health content.

---

### Dale-Chall Readability Formula

**Approach**: Uses a reference list of 3,000 words understood by at least 80% of 4th graders. Words not on the list are counted as "difficult."

**Formula**:
- 0.1579 × (percentage of difficult words) + 0.0496 × (words/sentences)
- Add 3.6365 if the percentage of difficult words exceeds 5%

**Score interpretation**:

| Score | Reading Level |
|-------|--------------|
| 4.9 and below | 4th grade and below |
| 5.0–5.9 | 5th–6th grade |
| 6.0–6.9 | 7th–8th grade |
| 7.0–7.9 | 9th–10th grade |
| 8.0–8.9 | 11th–12th grade |
| 9.0–9.9 | College level |
| 10.0+ | College graduate level |

**Best for**: Consumer-facing documents, plain language assessment, content where vocabulary difficulty is the primary concern.

**Notes**:
- More vocabulary-focused than sentence-length-focused.
- Useful alongside Flesch-Kincaid for a complete picture.

---

## Grade Level Interpretation

| Grade | Reading Level | Typical Use Cases |
|-------|--------------|-------------------|
| 4–5 | Simple, everyday language | Patient materials, consumer product labels, children's content |
| 6–8 | Clear, accessible prose | Government communications, user guides, help articles |
| 8–10 | Standard professional writing | Business communications, general audience documentation |
| 10–12 | Advanced professional | Technical manuals, legal summaries, policy documents |
| 12–14 | Specialized professional | Academic papers, developer documentation, clinical guidelines |
| 14+ | Expert only | Research papers, legal statutes, advanced scientific literature |

---

## Word Substitution Guide

Replace complex words with simpler alternatives. Default to the simpler word unless the complex word adds precision that matters to the audience.

| Complex | Simple |
|---------|--------|
| utilize | use |
| approximately | about |
| demonstrate | show |
| implement | build, set up |
| functionality | feature |
| subsequently | then, next |
| in order to | to |
| facilitate | help, enable |
| commence | start, begin |
| terminate | end, stop |
| endeavor | try |
| prior to | before |
| regarding | about |
| sufficient | enough |
| numerous | many |
| methodology | method |
| component | part |
| leverage | use |
| paradigm | model, pattern |
| aforementioned | this, that |
| ascertain | find out, confirm |
| disseminate | share, send |
| enumerate | list |
| initiate | start |
| obtain | get |
| proceed | go, continue |
| require | need |
| submit | send |
| validate | check, confirm |
| via | through, by, using |

---

## Sentence Rewriting Strategies

### Break Compound Sentences

Long compound sentences slow reading and increase cognitive load. Break them into shorter, focused statements.

- **Before**: "The system processes the request and validates the input and returns a response."
- **After**: "The system processes the request. It validates the input. Then it returns a response."

---

### Front-Load the Action

Readers scan for what to do. Put the action or conclusion first, then explain context or rationale.

- **Before**: "In order to configure the system for optimal performance, administrators should adjust the memory allocation settings."
- **After**: "Adjust memory allocation settings to improve performance."

---

### Remove Nominalizations

Nominalizations turn verbs into nouns (implementation, utilization, configuration). They make sentences passive and abstract. Convert back to verb form.

- **Before**: "The implementation of the feature was completed by the team."
- **After**: "The team implemented the feature."

- **Before**: "Utilization of the API requires authentication."
- **After**: "To use the API, you must authenticate."

- **Before**: "Configuration of the settings is required before deployment."
- **After**: "Configure the settings before you deploy."

---

### Use Active Voice

Active voice identifies who does the action. Passive voice hides the actor and often creates wordier sentences.

- **Before**: "The report was generated by the system."
- **After**: "The system generated the report."

- **Before**: "Errors are logged to the console."
- **After**: "The system logs errors to the console."

- **Before**: "The form must be submitted before the deadline."
- **After**: "Submit the form before the deadline."

Note: Passive voice is acceptable in scientific methodology sections ("Samples were collected...") and in regulatory writing where the actor is irrelevant or unknown.

---

### Remove Hedge Words

Hedge words ("generally," "typically," "may potentially") weaken confidence and add length. Remove them unless the uncertainty is real and material to the reader.

- **Before**: "It is generally considered that this approach might potentially improve performance."
- **After**: "This approach improves performance."

- **Before**: "Users may possibly experience delays."
- **After**: "Users may experience delays." (keep if uncertainty is real)

- **Before**: "This is basically a way to sort of simplify the process."
- **After**: "This simplifies the process."

---

### Reduce Prepositional Chains

Multiple prepositional phrases in a row create long, hard-to-parse noun phrases.

- **Before**: "The configuration of the settings of the server in the production environment."
- **After**: "The production server's settings."

- **Before**: "The process of the submission of the form by the user."
- **After**: "The user submits the form."

---

### Eliminate Redundant Pairs

Many common phrases repeat the same idea twice.

| Redundant | Simple |
|-----------|--------|
| each and every | each / every |
| first and foremost | first |
| true and accurate | accurate |
| null and void | void |
| basic and fundamental | fundamental |
| various and sundry | various |
| full and complete | complete |
