#!/usr/bin/env python3
"""
Readability scoring tool for markdown and text files.

Computes Flesch-Kincaid Grade Level, Gunning Fog Index, SMOG Index, and
Dale-Chall score. Evaluates results against industry/audience-specific targets
and outputs a pass/fail report with actionable recommendations.

Usage:
    python3 readability.py FILE [--industry INDUSTRY] [--audience AUDIENCE] [--format json|text]
"""

import sys
import os
import re
import math
import json
import argparse


# ---------------------------------------------------------------------------
# Color support
# ---------------------------------------------------------------------------

USE_COLOR = sys.stdout.isatty()
GREEN  = '\033[92m' if USE_COLOR else ''
RED    = '\033[91m' if USE_COLOR else ''
YELLOW = '\033[93m' if USE_COLOR else ''
BOLD   = '\033[1m'  if USE_COLOR else ''
RESET  = '\033[0m'  if USE_COLOR else ''


# ---------------------------------------------------------------------------
# Target grade-level matrix
# ---------------------------------------------------------------------------

TARGETS = {
    ('medical', 'end-user'):       (4,  6),
    ('medical', 'regulatory'):     (8,  10),
    ('medical', 'developer'):      (10, 14),
    ('medical', 'general'):        (6,  8),
    ('tech', 'developer'):         (10, 14),
    ('tech', 'end-user'):          (6,  8),
    ('tech', 'executive'):         (8,  10),
    ('tech', 'general'):           (8,  10),
    ('tech', 'regulatory'):        (8,  10),
    ('financial', 'end-user'):     (6,  8),
    ('financial', 'general'):      (6,  8),
    ('financial', 'executive'):    (8,  10),
    ('financial', 'regulatory'):   (8,  10),
    ('financial', 'developer'):    (10, 14),
    ('gov', 'general'):            (6,  8),
    ('gov', 'end-user'):           (6,  8),
    ('gov', 'regulatory'):         (8,  10),
    ('gov', 'executive'):          (8,  10),
    ('gov', 'developer'):          (10, 14),
    ('legal', 'general'):          (8,  10),
    ('legal', 'end-user'):         (6,  8),
    ('legal', 'regulatory'):       (10, 12),
    ('legal', 'executive'):        (8,  10),
    ('legal', 'developer'):        (10, 14),
    ('engineering', 'developer'):  (10, 14),
    ('engineering', 'end-user'):   (6,  8),
    ('engineering', 'general'):    (8,  10),
    ('engineering', 'executive'):  (8,  10),
    ('engineering', 'regulatory'): (10, 12),
    ('academic', 'general'):       (12, 16),
    ('academic', 'developer'):     (12, 16),
    ('academic', 'end-user'):      (8,  10),
    ('academic', 'executive'):     (10, 12),
    ('academic', 'regulatory'):    (12, 16),
}

DEFAULT_TARGET = (8, 12)

# Abbreviations that should not be treated as sentence boundaries
ABBREVIATIONS = {
    'mr', 'mrs', 'ms', 'dr', 'prof', 'sr', 'jr', 'st', 'ave', 'blvd',
    'inc', 'corp', 'ltd', 'co', 'vs', 'etc', 'e.g', 'i.e', 'u.s', 'u.k',
}


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

def extract_text(raw: str) -> str:
    """Strip markdown syntax and return plain prose."""
    # Remove fenced code blocks (``` ... ```)
    text = re.sub(r'```[\s\S]*?```', ' ', raw)
    # Remove inline code (`...`)
    text = re.sub(r'`[^`]*`', ' ', text)
    # Remove images: ![alt](url) -> alt
    text = re.sub(r'!\[([^\]]*)\]\([^)]*\)', r'\1', text)
    # Remove links but keep text: [text](url) -> text
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Remove headings (leading # symbols)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic markers (**, __, *, _, ~~)
    text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)
    text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)
    text = re.sub(r'~~(.*?)~~', r'\1', text)
    # Remove horizontal rules (---, ***, ___)
    text = re.sub(r'^\s*[-*_]{3,}\s*$', ' ', text, flags=re.MULTILINE)
    # Remove list markers (-, *, 1.)
    text = re.sub(r'^\s*[-*]\s+', ' ', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', ' ', text, flags=re.MULTILINE)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ---------------------------------------------------------------------------
# Sentence splitting
# ---------------------------------------------------------------------------

def split_sentences(text: str) -> list:
    """Split text into sentences, respecting common abbreviations."""
    # Tokenize on sentence-ending punctuation followed by whitespace/EOF
    # Use a regex that captures the delimiter so we can reconstruct context
    raw_splits = re.split(r'(?<=[.!?])\s+', text)

    sentences = []
    buffer = ''
    for chunk in raw_splits:
        if buffer:
            candidate = buffer
        else:
            candidate = chunk
            buffer = ''

        if buffer:
            # Check if the last token of buffer looks like an abbreviation
            last_token = buffer.rstrip().split()[-1] if buffer.strip() else ''
            last_token_clean = last_token.rstrip('.').lower()
            if last_token_clean in ABBREVIATIONS or re.match(r'^[A-Z]$', last_token.rstrip('.')):
                # Merge with next chunk -- likely an abbreviation
                buffer = buffer + ' ' + chunk
                continue
            sentences.append(candidate)
            buffer = chunk
        else:
            buffer = chunk

    if buffer.strip():
        sentences.append(buffer)

    # Filter out empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences if sentences else [text]


# ---------------------------------------------------------------------------
# Word tokenization
# ---------------------------------------------------------------------------

def tokenize_words(text: str) -> list:
    """Split text into words, stripping surrounding punctuation."""
    raw_tokens = text.split()
    words = []
    for token in raw_tokens:
        # Strip leading/trailing punctuation but keep apostrophes and hyphens inside words
        token = re.sub(r"^[^\w''-]+", '', token)
        token = re.sub(r"[^\w''-]+$", '', token)
        if len(token) >= 1:
            words.append(token)
    return words


# ---------------------------------------------------------------------------
# Syllable counting
# ---------------------------------------------------------------------------

def count_syllables(word: str) -> int:
    """Estimate syllable count for a word using regex heuristics."""
    word = word.lower().strip()
    if len(word) <= 2:
        return 1
    # Remove trailing silent-e (but not -le)
    if word.endswith('e') and not word.endswith('le'):
        word = word[:-1]
    # Count vowel groups
    vowel_groups = re.findall(r'[aeiouy]+', word)
    count = len(vowel_groups)
    # Adjust for -le ending where preceding char is a consonant
    if word.endswith('le') and len(word) > 2 and word[-3] not in 'aeiouy':
        count += 1
    # Handle -ed endings (often silent)
    if word.endswith('ed') and len(word) > 3:
        if word[-3] not in 'dt':
            count -= 1
    return max(1, count)


# ---------------------------------------------------------------------------
# Dale-Chall word list
# ---------------------------------------------------------------------------

def load_dale_chall_words():
    """Load the Dale-Chall familiar word list from the references directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)
    word_file = os.path.join(skill_dir, 'references', 'dale-chall-words.txt')
    if not os.path.exists(word_file):
        return None
    with open(word_file) as f:
        return set(line.strip().lower() for line in f if line.strip())


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def compute_metrics(words: list, sentences: list, dale_chall_words) -> dict:
    """Compute all readability metrics and return a dict of scores."""
    total_words     = len(words)
    total_sentences = len(sentences)
    total_syllables = sum(count_syllables(w) for w in words)
    polysyllables   = sum(1 for w in words if count_syllables(w) >= 3)

    avg_words_per_sentence = total_words / total_sentences
    polysyllabic_pct       = (polysyllables / total_words) * 100 if total_words else 0

    # Flesch-Kincaid Grade Level
    fk = (
        0.39  * (total_words / total_sentences)
        + 11.8 * (total_syllables / total_words)
        - 15.59
    )

    # Gunning Fog Index
    complex_words = sum(
        1 for w in words
        if count_syllables(w) >= 3
        and not w.lower().endswith('ing')
        and not w.lower().endswith('ed')
        and not w.lower().endswith('es')
    )
    fog = 0.4 * (
        (total_words / total_sentences)
        + 100.0 * (complex_words / total_words)
    )

    # SMOG Index
    smog = 1.0430 * math.sqrt(polysyllables * (30.0 / total_sentences)) + 3.1291

    # Dale-Chall
    dc = None
    if dale_chall_words is not None:
        difficult    = sum(1 for w in words if w.lower() not in dale_chall_words)
        pct_difficult = (difficult / total_words) * 100
        dc = 0.1579 * pct_difficult + 0.0496 * (total_words / total_sentences)
        if pct_difficult > 5:
            dc += 3.6365

    return {
        'total_words':            total_words,
        'total_sentences':        total_sentences,
        'total_syllables':        total_syllables,
        'polysyllables':          polysyllables,
        'avg_words_per_sentence': avg_words_per_sentence,
        'polysyllabic_pct':       polysyllabic_pct,
        'flesch_kincaid':         round(fk, 1),
        'gunning_fog':            round(fog, 1),
        'smog':                   round(smog, 1),
        'dale_chall':             round(dc, 1) if dc is not None else None,
    }


# ---------------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------------

def generate_recommendations(metrics: dict, target_low: int, target_high: int) -> list:
    """Generate actionable recommendations based on metric results."""
    recs = []
    avg_sl     = metrics['avg_words_per_sentence']
    poly_pct   = metrics['polysyllabic_pct']

    if avg_sl > 20:
        recs.append(
            f"Average sentence length is {avg_sl:.1f} words. "
            "Target under 20 for this audience. Break long sentences into shorter ones."
        )

    if poly_pct > 15:
        recs.append(
            f"{poly_pct:.1f}% of words have 3+ syllables (target: under 15%). "
            "Use simpler alternatives: utilize\u2192use, approximately\u2192about, "
            "demonstrate\u2192show, implement\u2192build, functionality\u2192feature."
        )

    for metric_name, score in [
        ('Flesch-Kincaid', metrics['flesch_kincaid']),
        ('Gunning Fog',    metrics['gunning_fog']),
        ('SMOG',           metrics['smog']),
        ('Dale-Chall',     metrics['dale_chall']),
    ]:
        if score is None:
            continue
        if score > target_high:
            recs.append(
                f"{metric_name} grade level {score} exceeds target range "
                f"{target_low}-{target_high}. Simplify vocabulary and shorten sentences."
            )
        elif score < target_low:
            recs.append(
                f"{metric_name} grade level {score} is below target range "
                f"{target_low}-{target_high}. "
                "The content may be oversimplified for this audience."
            )

    return recs


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_text_output(
    filename: str,
    industry: str,
    audience: str,
    target_low: int,
    target_high: int,
    metrics: dict,
    recommendations: list,
) -> str:
    """Render the human-readable text report."""
    lines = []

    divider_thick = '\u2550' * 51
    divider_thin  = '\u2500' * 51

    lines.append(divider_thick)
    lines.append(f"{BOLD}Readability Analysis{RESET}")
    lines.append(divider_thick)
    lines.append('')
    lines.append(f"Document:  {os.path.basename(filename)}")
    lines.append(f"Industry:  {industry}")
    lines.append(f"Audience:  {audience}")
    lines.append(f"Target:    Grade {target_low}-{target_high}")
    lines.append('')
    lines.append("Statistics:")
    lines.append(f"  Words:      {metrics['total_words']:,}")
    lines.append(f"  Sentences:  {metrics['total_sentences']:,}")
    lines.append(f"  Avg words/sentence: {metrics['avg_words_per_sentence']:.1f}")
    lines.append(f"  Syllables:  {metrics['total_syllables']:,}")
    poly = metrics['polysyllables']
    poly_pct = metrics['polysyllabic_pct']
    lines.append(f"  Polysyllabic words: {poly:,} ({poly_pct:.1f}%)")
    lines.append('')
    lines.append(divider_thin)
    lines.append(f"{'Metric':<22} {'Score':<9} {'Target':<10} {'Status'}")
    lines.append(divider_thin)

    metric_rows = [
        ('Flesch-Kincaid GL',  metrics['flesch_kincaid']),
        ('Gunning Fog Index',  metrics['gunning_fog']),
        ('SMOG Index',         metrics['smog']),
        ('Dale-Chall',         metrics['dale_chall']),
    ]

    for label, score in metric_rows:
        if score is None:
            lines.append(f"{'Dale-Chall':<22} {'N/A':<9} {str(target_low)+'-'+str(target_high):<10} (word list not found)")
            continue
        passed = target_low <= score <= target_high
        status_str = f"{GREEN}\u2713 PASS{RESET}" if passed else f"{RED}\u2717 FAIL{RESET}"
        target_str = f"{target_low}-{target_high}"
        lines.append(f"{label:<22} {score:<9} {target_str:<10} {status_str}")

    lines.append(divider_thin)

    if recommendations:
        lines.append('')
        lines.append("Recommendations:")
        for rec in recommendations:
            # Word-wrap at ~72 chars with bullet prefix
            words_rec = rec.split()
            current_line = "\u2022 "
            indent       = "  "
            for word in words_rec:
                if len(current_line) + len(word) + 1 > 72:
                    lines.append(current_line)
                    current_line = indent + word + ' '
                else:
                    current_line += word + ' '
            if current_line.strip():
                lines.append(current_line.rstrip())

    return '\n'.join(lines)


def format_json_output(
    filename: str,
    industry: str,
    audience: str,
    target_low: int,
    target_high: int,
    metrics: dict,
    recommendations: list,
) -> str:
    """Render the JSON report."""

    def metric_obj(score):
        if score is None:
            return None
        return {
            'score': score,
            'pass':  target_low <= score <= target_high,
        }

    overall_pass = all(
        target_low <= s <= target_high
        for s in [
            metrics['flesch_kincaid'],
            metrics['gunning_fog'],
            metrics['smog'],
        ]
        if s is not None
    )
    if metrics['dale_chall'] is not None:
        overall_pass = overall_pass and (target_low <= metrics['dale_chall'] <= target_high)

    payload = {
        'document':    os.path.basename(filename),
        'industry':    industry,
        'audience':    audience,
        'target_grade': [target_low, target_high],
        'statistics': {
            'words':                metrics['total_words'],
            'sentences':            metrics['total_sentences'],
            'avg_words_per_sentence': round(metrics['avg_words_per_sentence'], 1),
            'syllables':            metrics['total_syllables'],
            'polysyllabic_words':   metrics['polysyllables'],
            'polysyllabic_pct':     round(metrics['polysyllabic_pct'], 1),
        },
        'metrics': {
            'flesch_kincaid': metric_obj(metrics['flesch_kincaid']),
            'gunning_fog':    metric_obj(metrics['gunning_fog']),
            'smog':           metric_obj(metrics['smog']),
            'dale_chall':     metric_obj(metrics['dale_chall']),
        },
        'overall_pass':    overall_pass,
        'recommendations': recommendations,
    }
    return json.dumps(payload, indent=2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Readability scoring tool for markdown and text files.'
    )
    parser.add_argument(
        'file',
        metavar='FILE',
        help='Path to the markdown or text file to analyze.',
    )
    parser.add_argument(
        '--industry',
        choices=['tech', 'medical', 'legal', 'financial', 'gov', 'engineering', 'academic'],
        default='tech',
        help='Target industry (default: tech).',
    )
    parser.add_argument(
        '--audience',
        choices=['executive', 'developer', 'end-user', 'regulatory', 'general'],
        default='general',
        help='Target audience (default: general).',
    )
    parser.add_argument(
        '--format',
        choices=['json', 'text'],
        default='text',
        dest='output_format',
        help='Output format (default: text).',
    )
    args = parser.parse_args()

    # --- File loading -------------------------------------------------------
    if not os.path.exists(args.file):
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(2)

    with open(args.file, encoding='utf-8', errors='replace') as fh:
        raw = fh.read()

    # --- Processing ---------------------------------------------------------
    plain_text      = extract_text(raw)
    sentences       = split_sentences(plain_text)
    words           = tokenize_words(plain_text)

    if not words:
        print("Error: no readable text found in file.", file=sys.stderr)
        sys.exit(1)

    dale_chall_words = load_dale_chall_words()
    metrics          = compute_metrics(words, sentences, dale_chall_words)

    target_low, target_high = TARGETS.get(
        (args.industry, args.audience), DEFAULT_TARGET
    )

    recommendations = generate_recommendations(metrics, target_low, target_high)

    # --- Output -------------------------------------------------------------
    if args.output_format == 'json':
        print(format_json_output(
            args.file, args.industry, args.audience,
            target_low, target_high, metrics, recommendations,
        ))
    else:
        print(format_text_output(
            args.file, args.industry, args.audience,
            target_low, target_high, metrics, recommendations,
        ))

    # --- Exit code ----------------------------------------------------------
    scores = [
        metrics['flesch_kincaid'],
        metrics['gunning_fog'],
        metrics['smog'],
    ]
    if metrics['dale_chall'] is not None:
        scores.append(metrics['dale_chall'])

    all_pass = all(target_low <= s <= target_high for s in scores if s is not None)
    sys.exit(0 if all_pass else 1)


if __name__ == '__main__':
    main()
