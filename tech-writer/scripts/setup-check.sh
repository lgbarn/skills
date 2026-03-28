#!/usr/bin/env bash
# Tech Writer - Dependency Checker
# Verifies all required tools are present and reports versions.
# Non-destructive: never installs anything, only reports.
#
# Usage: bash setup-check.sh
# Exit codes: 0 = all pass, 1 = one or more missing

set -euo pipefail

# Colors
if [[ -t 1 ]]; then
  GREEN='\033[92m'
  RED='\033[91m'
  YELLOW='\033[93m'
  BOLD='\033[1m'
  RESET='\033[0m'
else
  GREEN='' RED='' YELLOW='' BOLD='' RESET=''
fi

PASS=0
FAIL=0

check() {
  local name="$1"
  local cmd="$2"
  local version_cmd="${3:-}"
  local required="${4:-true}"

  if command -v "$cmd" &>/dev/null; then
    local version=""
    if [[ -n "$version_cmd" ]]; then
      version=$( eval "$version_cmd" 2>/dev/null | head -1 ) || version="(version unknown)"
    fi
    printf "  ${GREEN}✓${RESET} %-20s %s\n" "$name" "$version"
    PASS=$((PASS + 1))
  else
    if [[ "$required" == "true" ]]; then
      printf "  ${RED}✗${RESET} %-20s ${RED}not found${RESET}\n" "$name"
      FAIL=$((FAIL + 1))
    else
      printf "  ${YELLOW}○${RESET} %-20s ${YELLOW}not found (optional)${RESET}\n" "$name"
    fi
  fi
}

check_latex_pkg() {
  local pkg="$1"
  if kpsewhich "${pkg}.sty" &>/dev/null; then
    printf "  ${GREEN}✓${RESET} %-20s found\n" "$pkg"
    PASS=$((PASS + 1))
  else
    printf "  ${RED}✗${RESET} %-20s ${RED}not found${RESET}\n" "$pkg"
    FAIL=$((FAIL + 1))
  fi
}

echo ""
echo "${BOLD}Tech Writer - Dependency Check${RESET}"
echo "═══════════════════════════════════════════"
echo ""

echo "${BOLD}Core Tools${RESET}"
check "pandoc"    "pandoc"    "pandoc --version | head -1"
check "python3"   "python3"  "python3 --version"
echo ""

echo "${BOLD}PDF Engines${RESET}"
check "xelatex"   "xelatex"  "xelatex --version | head -1"
check "pdflatex"  "pdflatex" "pdflatex --version | head -1"  "false"
check "lualatex"  "lualatex" "lualatex --version | head -1"  "false"
echo ""

echo "${BOLD}LaTeX Packages${RESET}"
if command -v kpsewhich &>/dev/null; then
  check_latex_pkg "geometry"
  check_latex_pkg "fontspec"
  check_latex_pkg "fancyhdr"
  check_latex_pkg "hyperref"
  check_latex_pkg "xcolor"
  check_latex_pkg "framed"
else
  printf "  ${YELLOW}○${RESET} %-20s ${YELLOW}kpsewhich not available, cannot check packages${RESET}\n" "(skipped)"
fi
echo ""

echo "═══════════════════════════════════════════"
if [[ $FAIL -eq 0 ]]; then
  echo "${GREEN}${BOLD}All $PASS required dependencies found.${RESET}"
  exit 0
else
  echo "${RED}${BOLD}$FAIL dependency/ies missing. $PASS found.${RESET}"
  exit 1
fi
