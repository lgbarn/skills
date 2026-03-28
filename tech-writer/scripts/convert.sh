#!/usr/bin/env bash
# =============================================================================
# convert.sh — Deterministic pandoc wrapper for tech-writer skill
#
# Purpose:
#   Converts markdown source files to various output formats (HTML, PDF, DOCX,
#   EPUB, ODT) using pandoc. Every pandoc parameter is explicitly set so that
#   output is fully reproducible regardless of the caller's environment.
#
# Usage:
#   convert.sh --input FILE --output FILE --target TARGET [OPTIONS]
#
# Required parameters:
#   --input FILE        Source markdown file
#   --output FILE       Output file (format detected from extension)
#   --target TARGET     Rendering target: web|print|pdf-screen|mobile|tablet
#
# Optional parameters:
#   --industry IND      tech|medical|legal|financial|gov|engineering|academic
#                       (default: tech)
#   --audience AUD      executive|developer|end-user|regulatory|general
#                       (default: general)
#   --grade-level N     Override Flesch-Kincaid grade level target (documented
#                       only; not passed to pandoc)
#   --toc               Include a table of contents
#   --numbered          Number sections
#   --paper-size SIZE   a4|letter (default: letter)
#   --lang LANG         BCP 47 language code (default: en)
#
# Exit codes:
#   0  Success
#   1  Bad or missing parameters
#   2  Input file not found
#   3  pandoc conversion failed
#   4  Unsupported output format
#
# To make this script executable after writing:
#   chmod +x convert.sh
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Directory resolution — locate assets relative to this script, not the caller
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
ASSETS_DIR="$SKILL_DIR/assets"
TEMPLATES_DIR="$ASSETS_DIR/templates"
FILTERS_DIR="$ASSETS_DIR/pandoc/filters"

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
INPUT=""
OUTPUT=""
TARGET=""
INDUSTRY="tech"
AUDIENCE="general"
GRADE_LEVEL=""
TOC="false"
NUMBERED="false"
PAPER_SIZE="letter"
LANG="en"

# ---------------------------------------------------------------------------
# usage — print help and exit 1
# ---------------------------------------------------------------------------
usage() {
  cat >&2 <<EOF
Usage: $(basename "$0") --input FILE --output FILE --target TARGET [OPTIONS]

Required:
  --input FILE        Source markdown file
  --output FILE       Output file (format detected from extension)
  --target TARGET     web | print | pdf-screen | mobile | tablet

Optional:
  --industry IND      tech | medical | legal | financial | gov |
                      engineering | academic  (default: tech)
  --audience AUD      executive | developer | end-user | regulatory |
                      general  (default: general)
  --grade-level N     Target Flesch-Kincaid grade level (documented only;
                      not passed to pandoc)
  --toc               Include a table of contents
  --numbered          Number sections
  --paper-size SIZE   a4 | letter  (default: letter)
  --lang LANG         BCP 47 language code  (default: en)

Supported output extensions:
  .html  .pdf  .docx  .epub  .odt

Exit codes:
  0  Success
  1  Bad or missing parameters
  2  Input file not found
  3  pandoc conversion failed
  4  Unsupported output format
EOF
  exit 1
}

# ---------------------------------------------------------------------------
# Parse CLI arguments
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --input)
      INPUT="$2"
      shift 2
      ;;
    --output)
      OUTPUT="$2"
      shift 2
      ;;
    --target)
      TARGET="$2"
      shift 2
      ;;
    --industry)
      INDUSTRY="$2"
      shift 2
      ;;
    --audience)
      AUDIENCE="$2"
      shift 2
      ;;
    --grade-level)
      GRADE_LEVEL="$2"
      shift 2
      ;;
    --toc)
      TOC="true"
      shift
      ;;
    --numbered)
      NUMBERED="true"
      shift
      ;;
    --paper-size)
      PAPER_SIZE="$2"
      shift 2
      ;;
    --lang)
      LANG="$2"
      shift 2
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo "Error: Unknown parameter '$1'" >&2
      usage
      ;;
  esac
done

# ---------------------------------------------------------------------------
# Validate required parameters
# ---------------------------------------------------------------------------
if [[ -z "$INPUT" ]]; then
  echo "Error: --input is required" >&2
  usage
fi

if [[ -z "$OUTPUT" ]]; then
  echo "Error: --output is required" >&2
  usage
fi

if [[ -z "$TARGET" ]]; then
  echo "Error: --target is required" >&2
  usage
fi

# ---------------------------------------------------------------------------
# Validate input file exists
# ---------------------------------------------------------------------------
if [[ ! -f "$INPUT" ]]; then
  echo "Error: Input file not found: $INPUT" >&2
  exit 2
fi

# ---------------------------------------------------------------------------
# Detect output format from file extension
# ---------------------------------------------------------------------------
OUTPUT_EXT="${OUTPUT##*.}"
case "$OUTPUT_EXT" in
  html) OUTPUT_FORMAT="html5" ;;
  pdf)  OUTPUT_FORMAT="pdf" ;;
  docx) OUTPUT_FORMAT="docx" ;;
  epub) OUTPUT_FORMAT="epub" ;;
  odt)  OUTPUT_FORMAT="odt" ;;
  *)    echo "Error: Unsupported output format '.$OUTPUT_EXT'" >&2; exit 4 ;;
esac

# ---------------------------------------------------------------------------
# Begin building the pandoc command array
# ---------------------------------------------------------------------------
CMD=(pandoc)

# -- Base options (always set) -----------------------------------------------
CMD+=(--from markdown --to "$OUTPUT_FORMAT")
CMD+=(--standalone)
CMD+=(-M "lang=$LANG")
CMD+=("$INPUT" -o "$OUTPUT")

# -- TOC and section numbering -----------------------------------------------
[[ "$TOC" == "true" ]] && CMD+=(--toc --toc-depth=3)
[[ "$NUMBERED" == "true" ]] && CMD+=(--number-sections)

# ---------------------------------------------------------------------------
# Target-specific options
# ---------------------------------------------------------------------------
case "$TARGET" in
  web)
    CMD+=(--embed-resources)
    CMD+=(-c "$TEMPLATES_DIR/web.css")
    CMD+=(-M "pagetitle=$(basename "$INPUT" .md)")
    ;;

  print)
    # print target only applies to PDF output
    if [[ "$OUTPUT_FORMAT" == "pdf" ]]; then
      CMD+=(--pdf-engine=xelatex)
      CMD+=(-V "fontsize=11pt")
      CMD+=(-V "documentclass=article")
      CMD+=(-V "classoption=oneside")
      CMD+=(-V "linestretch=1.25")
      if [[ "$PAPER_SIZE" == "a4" ]]; then
        CMD+=(-V "papersize=a4" -V "geometry=margin=25mm")
      else
        CMD+=(-V "papersize=letter" -V "geometry=margin=1in")
      fi
    fi
    ;;

  pdf-screen)
    # pdf-screen target only applies to PDF output
    if [[ "$OUTPUT_FORMAT" == "pdf" ]]; then
      CMD+=(--pdf-engine=xelatex)
      CMD+=(-V "fontsize=11pt")
      CMD+=(-V "documentclass=article")
      CMD+=(-V "classoption=oneside")
      CMD+=(-V "linestretch=1.15")
      CMD+=(-V "colorlinks=true" -V "linkcolor=NavyBlue" -V "urlcolor=NavyBlue" -V "citecolor=NavyBlue")
      if [[ "$PAPER_SIZE" == "a4" ]]; then
        CMD+=(-V "papersize=a4" -V "geometry=margin=20mm")
      else
        CMD+=(-V "papersize=letter" -V "geometry=margin=0.75in")
      fi
    fi
    ;;

  mobile)
    CMD+=(--embed-resources)
    CMD+=(-c "$TEMPLATES_DIR/mobile.css")
    CMD+=(-M "pagetitle=$(basename "$INPUT" .md)")
    ;;

  tablet)
    CMD+=(--embed-resources)
    CMD+=(-c "$TEMPLATES_DIR/web.css")
    CMD+=(-M "pagetitle=$(basename "$INPUT" .md)")
    ;;

  *)
    echo "Error: Unknown target '$TARGET'. Valid values: web|print|pdf-screen|mobile|tablet" >&2
    exit 1
    ;;
esac

# ---------------------------------------------------------------------------
# Industry overrides (applied after target; PDF formats only)
# ---------------------------------------------------------------------------
if [[ "$OUTPUT_FORMAT" == "pdf" ]]; then
  case "$INDUSTRY" in
    medical)
      CMD+=(-V 'mainfont=Times New Roman')
      CMD+=(-V "linestretch=1.5")
      ;;
    financial)
      CMD+=(-V 'mainfont=Arial')
      ;;
    legal)
      CMD+=(--number-sections)
      ;;
    gov)
      CMD+=(-V "fontsize=12pt")
      ;;
    # tech|engineering|academic — no PDF overrides needed
    tech|engineering|academic) ;;
    *)
      echo "Error: Unknown industry '$INDUSTRY'" >&2
      exit 1
      ;;
  esac
fi

# ---------------------------------------------------------------------------
# Audience overrides
# ---------------------------------------------------------------------------
case "$AUDIENCE" in
  developer)
    # Use syntax highlighting for developer audience; requires framed.sty for PDF
    if [[ "$OUTPUT_FORMAT" == "pdf" ]] && ! kpsewhich framed.sty &>/dev/null; then
      echo "WARNING: framed.sty not found; disabling code highlighting in PDF." >&2
      echo "  Install with: sudo tlmgr install framed" >&2
      CMD+=(--syntax-highlighting=none)
    else
      CMD+=(--syntax-highlighting=tango)
    fi
    ;;

  executive)
    # Wider margins for annotation space
    if [[ "$OUTPUT_FORMAT" == "pdf" ]]; then
      CMD+=(-V "geometry=left=1.5in,right=1.5in,top=1in,bottom=1in")
    fi
    ;;

  end-user)
    if [[ "$TOC" == "true" ]]; then
      # Override to a shallower TOC depth for non-technical readers
      CMD+=(--toc-depth=2)
    fi
    if [[ "$OUTPUT_FORMAT" == "pdf" ]]; then
      CMD+=(-V "fontsize=12pt")
    fi
    ;;

  regulatory)
    CMD+=(--number-sections)
    ;;

  # general — no additional overrides
  general) ;;

  *)
    echo "Error: Unknown audience '$AUDIENCE'" >&2
    exit 1
    ;;
esac

# ---------------------------------------------------------------------------
# Accessibility filter (HTML outputs only)
# Applied last so it sees the final document structure
# ---------------------------------------------------------------------------
if [[ "$OUTPUT_FORMAT" == "html5" ]] && [[ -f "$FILTERS_DIR/accessibility.lua" ]]; then
  CMD+=(-L "$FILTERS_DIR/accessibility.lua")
fi

# ---------------------------------------------------------------------------
# Log the exact command to stderr before executing
# ---------------------------------------------------------------------------
echo ">>> Running: ${CMD[*]}" >&2

# ---------------------------------------------------------------------------
# Execute pandoc
# ---------------------------------------------------------------------------
if "${CMD[@]}"; then
  echo "Output written to: $OUTPUT"
else
  echo "Error: pandoc conversion failed" >&2
  exit 3
fi
