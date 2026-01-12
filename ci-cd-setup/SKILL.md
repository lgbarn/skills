---
name: ci-cd-setup
description: Configure CI/CD pipelines, troubleshoot test failures, set up pre-commit hooks, and manage GitHub Actions for trading indicator development. Use when setting up testing infrastructure, diagnosing build failures, configuring branch protection, or running tests locally. Triggers: "CI failing", "set up tests", "pre-commit hooks", "GitHub Actions", "Docker testing".
allowed-tools: Read, Grep, Glob, Bash(git:*, docker:*, npm:*, pip:*, dotnet:*, pre-commit:*)
---

# CI/CD Setup Skill

Configure continuous integration and deployment for multi-platform trading indicators.

## Overview

This skill helps set up and manage:
- **Pre-commit hooks** - Run tests and linting before commits
- **GitHub Actions** - Automated CI/CD pipeline
- **Docker testing** - Isolated test environments
- **Branch protection** - Prevent failed tests from merging

---

## When to Use This Skill

**Use this skill when:**
- Setting up testing infrastructure for a new project
- Troubleshooting CI/CD pipeline failures
- Adding new test types or platforms
- Configuring pre-commit hooks
- Setting up branch protection rules
- Running tests locally before pushing

**Do NOT use for:**
- Writing indicator code (use indicator-generator skill)
- General Git operations (commits, branches, merges)
- Deployment to trading platforms

---

## Quick Commands

### Install Pre-commit Hooks
```bash
# Install pre-commit framework
pip install pre-commit

# Install hooks in this repository
pre-commit install

# Run all checks manually
pre-commit run --all-files
```

### Run Tests Locally
```bash
# NinjaTrader C# tests
dotnet test Ninjatrader/Tests/LB.Indicators.Tests.csproj --verbosity normal

# Tradovate JavaScript linting
npm install && npm run lint

# Pine Script validation
./scripts/validate-pine.sh Tradingview/*.pine
```

### Docker Testing
```bash
# Run all tests in Docker
docker-compose -f docker-compose.test.yml up --build

# Run only .NET tests
docker-compose -f docker-compose.test.yml up dotnet-tests --build

# Run only ESLint
docker-compose -f docker-compose.test.yml up eslint --build
```

---

## Configuration Files

| File | Purpose |
|------|---------|
| `.pre-commit-config.yaml` | Pre-commit hooks configuration |
| `.github/workflows/ci.yml` | GitHub Actions CI pipeline |
| `Dockerfile.dotnet` | Docker image for .NET tests |
| `docker-compose.test.yml` | Multi-service test orchestration |
| `scripts/validate-pine.sh` | Pine Script validation script |
| `.eslintrc.json` | ESLint config for Tradovate JS |
| `package.json` | Node.js dependencies |

---

## GitHub Actions Workflow

The CI pipeline runs on:
- Push to `main` or `develop` branches
- Pull requests targeting `main`

### Jobs

1. **pre-commit** - General code quality checks
2. **dotnet-test** - NinjaTrader tests (.NET 8.0, 9.0 matrix)
3. **eslint** - Tradovate JavaScript linting
4. **pine-validate** - Pine Script syntax validation
5. **status-gate** - All-jobs-must-pass gate

### Artifacts

Test results are uploaded as artifacts with 30-day retention.

---

## Branch Protection Setup

After pushing CI configuration to GitHub:

1. Go to **Settings > Branches > main**
2. Click **Add rule** or edit existing
3. Enable:
   - **Require status checks to pass before merging**
   - Select required checks:
     - `CI Status Gate`
     - `NinjaTrader Tests (.NET 9.0.x)`
   - **Require branches to be up to date before merging**
4. Optionally enable:
   - **Require pull request reviews before merging**
   - **Do not allow bypassing the above settings**

---

## Test Infrastructure

### NinjaTrader Tests

Location: `Ninjatrader/Tests/`

```
Tests/
├── LB.Indicators.Tests.csproj    # Test project file
├── *HelperTests.cs               # Test files
└── Helpers/
    └── *Helpers.cs               # Extracted testable helpers
```

Test pattern: Helper Class Pattern
- Extract business logic to testable helper classes
- No NinjaTrader platform dependencies
- Pure C# unit tests with NUnit

### Pine Script Validation

The `scripts/validate-pine.sh` script checks:
- Version header (`//@version=5` or `//@version=6`)
- Author attribution for `LB_*` files
- `indicator()` or `strategy()` declaration
- Resource limits for Pro indicators
- Balanced brackets/parentheses
- No debug code left in

### Tradovate Linting

ESLint rules in `.eslintrc.json`:
- CommonJS module support
- No unused variables (except Tradovate patterns)
- Semicolons required
- Double quotes for strings
- No dangerous eval patterns

---

## Troubleshooting

### Pre-commit Errors

```bash
# Skip a specific hook temporarily
SKIP=dotnet-test pre-commit run --all-files

# Update hooks to latest versions
pre-commit autoupdate

# Clean and reinstall
pre-commit clean
pre-commit install
```

### .NET Test Failures

```bash
# Run with verbose output
dotnet test Ninjatrader/Tests/LB.Indicators.Tests.csproj --verbosity detailed

# Run specific test
dotnet test --filter "FullyQualifiedName~VWAPCalculatorTests"
```

### Docker Issues

```bash
# Rebuild without cache
docker-compose -f docker-compose.test.yml build --no-cache

# View logs
docker-compose -f docker-compose.test.yml logs
```

---

## Adding New Tests

When adding a new indicator:

1. Create helper class in `Ninjatrader/Tests/Helpers/`
2. Create test file in `Ninjatrader/Tests/`
3. Run tests locally: `dotnet test`
4. Commit and push - CI will validate

See `.claude/skills/indicator-generator/ninja/TESTING.md` for TDD workflow.

---

## CI/CD Maintenance

### Update Dependencies

```bash
# Update pre-commit hooks
pre-commit autoupdate

# Update npm dependencies
npm update

# Update .NET dependencies (in test project)
dotnet outdated Ninjatrader/Tests/LB.Indicators.Tests.csproj
```

### Monitor CI Status

- Check GitHub Actions tab for workflow runs
- Review test artifacts for detailed results
- Monitor code coverage trends

---

## Files Modified by This Skill

- `.pre-commit-config.yaml` - Pre-commit configuration
- `.github/workflows/ci.yml` - GitHub Actions workflow
- `Dockerfile.dotnet` - Docker test image
- `docker-compose.test.yml` - Docker Compose config
- `scripts/validate-pine.sh` - Pine Script validator
- `.eslintrc.json` - ESLint configuration
- `package.json` - Node.js dependencies
