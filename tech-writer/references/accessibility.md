# Accessibility Reference

WCAG 2.1 Level AA checklist and implementation guidance for documentation.

---

## WCAG 2.1 Level AA Checklist for Documentation

### Heading Hierarchy

- Start with H1. Proceed sequentially: H1 → H2 → H3 → H4.
- Never skip heading levels (no H1 → H3, no H2 → H4).
- Use exactly one H1 per page or document.
- Headings must describe the section content. Avoid generic headings like "Overview," "Section 1," or "Introduction" when a more specific label is possible.
- Headings are navigation landmarks for screen reader users. Every major section needs one.

**Correct hierarchy:**
```
H1: Setting Up Authentication
  H2: Prerequisites
  H2: Configure the OAuth Provider
    H3: Create an Application
    H3: Copy the Client Credentials
  H2: Test the Integration
```

**Incorrect (skipped level):**
```
H1: Setting Up Authentication
  H3: Configure the OAuth Provider   ← skips H2
```

---

### Images and Media

**Alt text rules:**
- All informative images require alt text that describes the content and its purpose in context.
- Decorative images (purely visual, no informational content): use an empty alt attribute (`alt=""`). This tells screen readers to skip the image.
- Functional images (buttons, icons with a purpose): describe the function, not the appearance. Alt text for a search icon button: "Search" not "magnifying glass."

**Complex images:**
- Charts, diagrams, and infographics require a text description that conveys the same information.
- Options: caption below the image, a linked description page, or a `<figure>` with `<figcaption>`.
- The alt text for a complex image should summarize the key finding: "Bar chart showing Q3 revenue increased 22% year over year."

**Text in images:**
- Avoid placing text in images. If unavoidable, the alt text must duplicate the full text of the image.

**Video and audio:**
- All video content requires captions (synchronized text of all spoken words and relevant non-speech audio).
- All audio-only content requires a full transcript.
- Captions and transcripts must be accurate — auto-generated captions require human review and correction.

---

### Color and Contrast

**Contrast ratios (WCAG 2.1 Level AA):**
- Normal text (under 18pt regular, under 14pt bold): minimum 4.5:1 contrast ratio against the background.
- Large text (18pt+ regular or 14pt+ bold): minimum 3:1 contrast ratio.
- UI components and graphical objects (icons, borders, chart lines): minimum 3:1 against adjacent colors.

**Never convey information by color alone.** Always pair color with a secondary indicator:
- Error states: red color + an error icon + error text.
- Required fields: colored asterisk + the word "required."
- Chart series: different colors + different line patterns or data point shapes.
- Status indicators: colored dot + a text label.

**Testing tools:**
- WebAIM Contrast Checker (webaim.org/resources/contrastchecker)
- Browser DevTools accessibility panel
- Colour Contrast Analyser (desktop app, free)

---

### Tables

- Use `<caption>` to provide a table title. Do not use a heading above the table as a substitute.
- Mark header cells with `<th>` instead of `<td>`.
- Use `scope="col"` for column headers and `scope="row"` for row headers.
- Never use tables for page layout. Tables are for tabular data only.
- Keep tables simple. Avoid merged cells (`colspan`, `rowspan`) when possible — they disrupt screen reader navigation.
- For complex tables that require merged cells, add a `summary` attribute or an associated description explaining the table structure.

**Example markup:**
```html
<table>
  <caption>API Response Codes</caption>
  <thead>
    <tr>
      <th scope="col">Code</th>
      <th scope="col">Meaning</th>
      <th scope="col">Action</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>200</td>
      <td>Success</td>
      <td>Continue processing</td>
    </tr>
  </tbody>
</table>
```

---

### Links

- Link text must describe the destination or action. Never use "click here," "read more," or "learn more" as the full link text.
- Context rule: link text should make sense when read out of context (screen readers list all links on a page).
  - Bad: "For more information, [click here]."
  - Good: "[Read the API authentication guide]."
- Distinguish links from surrounding text by underline in addition to color. Color alone is not sufficient.
- If a link opens in a new tab or window, indicate this in the link text or with an icon + alt text: "API reference (opens in new tab)."
- Avoid duplicate link text for different destinations on the same page.

---

### Language Declaration

**Document language:**
- HTML: `<html lang="en">`
- Markdown with front matter: `lang: en`
- PDF: Set document language in metadata/properties.

**Inline language changes:**
- Mark any passage in a different language: `<span lang="fr">bonjour</span>`
- This allows screen readers to switch to the appropriate pronunciation.

---

### Reading Order

- The visual reading order must match the DOM (source code) order.
- Do not use CSS to visually reorder content that is logically ordered differently in the source.
- Use semantic HTML elements to define structure:
  - `<article>` for self-contained content
  - `<section>` for grouped content within a page
  - `<nav>` for navigation blocks
  - `<aside>` for supplementary content (sidebars, callouts)
  - `<main>` for the primary page content
- Test reading order by disabling CSS and confirming the content reads logically top to bottom.

---

### Keyboard Navigation

- All interactive elements (links, buttons, form fields, dropdowns) must be operable with a keyboard alone.
- Tab order must follow the visual layout logically (left to right, top to bottom in LTR languages).
- Every focusable element must display a visible focus indicator when focused with the keyboard. Do not suppress the browser's default `:focus` outline unless a custom indicator is provided.
- No keyboard trap: users must be able to navigate into and out of every component using standard keys (Tab, Shift+Tab, Escape, arrow keys).

---

### PDF Accessibility (PDF/UA Standard)

PDFs require additional accessibility work beyond the source document.

**Required:**
- Tag all content elements: headings, paragraphs, lists, tables, figures.
- Set the document title in File > Properties > Description.
- Specify the document language in File > Properties > Advanced.
- Provide alt text for all images.
- Ensure a logical reading order in the Tags panel.
- Use actual text, not images of text (scanned documents must be OCR-processed).

**Microsoft Word to PDF:**
- Use the built-in "Save as PDF" or "Export to PDF" with "Document structure tags for accessibility" checked.
- Check the accessibility checker in Word before exporting.

**Adobe Acrobat:**
- Run the accessibility checker (Tools > Accessibility > Full Check).
- Fix all errors and review all warnings before publishing.

---

### Testing Approach

A complete accessibility check requires both automated and manual testing.

**Automated testing (catches ~30% of issues):**
- Run axe DevTools or WAVE on web-based documentation.
- Run the built-in accessibility checker in Word, PowerPoint, or Acrobat for document formats.

**Manual testing (required for full coverage):**

1. **Screen reader test**: Read the full document with VoiceOver (macOS: Command+F5) or NVDA (Windows, free). Confirm all content is read, all images have meaningful alt text, and headings provide useful navigation.

2. **Keyboard-only navigation**: Unplug your mouse. Navigate the entire document using only Tab, Shift+Tab, Enter, and arrow keys. Confirm all functionality is reachable and operable.

3. **Heading check**: Use a browser extension or screen reader heading list to review all headings. Confirm hierarchy is logical and every heading is descriptive.

4. **Color contrast check**: Sample foreground and background colors for all body text, headings, and UI elements using a contrast checker tool.

5. **Link text review**: List all links on the page. Confirm each link text is descriptive when read in isolation.

6. **Zoom test**: Zoom to 200%. Confirm text reflows and no content is lost or overlapping.
