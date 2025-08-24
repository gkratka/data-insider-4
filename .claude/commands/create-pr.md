# Create PR Command

---
description: "Create a comprehensive pull request with proper formatting, testing, and documentation"
allowed-tools: 
  - Bash(git:*)
  - Bash(gh:*)
  - Bash(npm:*)
  - Bash(yarn:*)
  - Write
  - Edit
---

# Create Pull Request

Create a comprehensive pull request for the current changes with proper formatting, testing, and documentation.

## Pre-flight Checks

Before creating the PR, perform these essential checks:

1. **Current Status Assessment**
   - Check current git status: `git status`
   - Review staged and unstaged changes: `git diff HEAD`
   - Identify current branch: `git branch --show-current`
   - Review recent commits: `git log --oneline -10`

2. **Code Quality Verification**
   - Run linting checks (adapt to your project's setup)
   - Execute test suite to ensure all tests pass
   - Check TypeScript compilation (if applicable)
   - Verify code formatting standards

3. **Documentation Updates**
   - Update relevant documentation files
   - Add/update inline code comments where necessary
   - Update CHANGELOG.md if it exists

## PR Creation Process

Follow these steps to create a high-quality pull request:

### 1. Branch Management
- Ensure you're on a feature branch (not main/master)
- If on main branch, create a new feature branch: `git checkout -b feature/descriptive-name`
- Ensure branch is up to date with main: `git fetch origin && git merge origin/main`

### 2. Commit Preparation
- Stage all relevant changes: `git add .`
- Create a meaningful commit message following conventional commit format:

### 3. Push and PR Creation
- Push branch to remote: `git push origin HEAD`
- Create PR using GitHub CLI: `gh pr create`

## PR Title and Description Template

Use this template for consistent PR formatting:

### Title Format

### Description Template
```markdown
## Summary
Brief overview of what this PR accomplishes.

## Changes Made
- [ ] List specific changes
- [ ] Include any new features
- [ ] Note any fixes or improvements

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Edge cases considered

## Documentation
- [ ] Code comments updated
- [ ] README updated (if needed)
- [ ] API documentation updated (if applicable)

## Breaking Changes
- [ ] No breaking changes
- [ ] Breaking changes documented below

## Additional Notes
Any additional context, screenshots, or notes for reviewers.

## Checklist
- [ ] Self-review completed
- [ ] Code follows project style guidelines
- [ ] Tests added/updated for new functionality
- [ ] Documentation updated
- [ ] No console errors or warnings