# Contributing to Vector Space

This project is maintained by a small team. Use this workflow to avoid merge conflicts and keep `main` stable.

## Team Workflow

1. Sync your local `main` branch:

```bash
git checkout main
git pull origin main
```

2. Create a feature branch from `main`:

```bash
git checkout -b feature/short-description
```

3. Make changes in small commits:

```bash
git add -A
git commit -m "feat: short, clear message"
```

4. Push your branch:

```bash
git push -u origin feature/short-description
```

5. Open a Pull Request (PR) to merge into `main`.

6. Request at least one review from your teammate.

7. Rebase or merge latest `main` before final merge if needed:

```bash
git checkout feature/short-description
git fetch origin
git rebase origin/main
```

## Branch Naming

Use one of these prefixes:

- `feature/...` for new features
- `fix/...` for bug fixes
- `chore/...` for maintenance
- `docs/...` for docs only
- `test/...` for test updates

Examples:

- `feature/marketplace-filters`
- `fix/dashboard-role-redirect`
- `docs/team-workflow`

## Commit Message Style

Use conventional prefixes:

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation changes
- `test:` test changes
- `refactor:` code cleanup without behavior change
- `chore:` tooling/config updates

Examples:

- `feat: add recruiter dashboard stats`
- `fix: enforce role check in mentorship view`

## Pull Request Rules

- Keep PRs focused on one topic.
- Link the related issue/task when possible.
- Include screenshots for UI changes.
- Add or update tests for behavior changes.
- Do not push directly to `main`.

## Conflict-Safe Daily Routine

1. Start day: `git checkout main` and `git pull origin main`.
2. Work only in your own branch.
3. Push often.
4. Before opening PR, update branch from `origin/main`.
5. Resolve conflicts locally, run tests, then push.

## Recommended Review Checklist

- Does it solve the intended problem?
- Any role-based access regressions?
- URL namespacing and redirects still correct?
- Tests cover the change?
- No secrets or local artifacts added?

## Live Collaboration

For pair programming, use VS Code Live Share.

- Install extension: `ms-vsliveshare.vsliveshare`
- Host starts session and shares invite link
- Keep PR workflow for final merge history
