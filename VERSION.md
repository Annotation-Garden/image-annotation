# Version Management

Image Annotation Dashboard follows [Semantic Versioning 2.0.0](https://semver.org/).

## Current Version

**0.2.0-beta**

## Version Format

```
MAJOR.MINOR.PATCH[-PRERELEASE]
```

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backwards-compatible)
- **PATCH**: Bug fixes (backwards-compatible)
- **PRERELEASE**: Optional pre-release label
  - `alpha`: Early testing, may have significant bugs
  - `beta`: Feature-complete, testing and refinement
  - `rc`: Release candidate, final testing before stable
  - Omitted for stable releases (e.g., `1.0.0`)

## Bumping Version

Use the version bump script to increment the version:

```bash
# Patch version bump (0.1.4-beta -> 0.1.5-beta)
python scripts/bump_version.py patch

# Minor version bump (0.1.4-beta -> 0.2.0-beta)
python scripts/bump_version.py minor

# Major version bump (0.1.4-beta -> 1.0.0-beta)
python scripts/bump_version.py major

# Change pre-release label
python scripts/bump_version.py patch --prerelease rc    # -> 0.1.5-rc
python scripts/bump_version.py minor --prerelease stable # -> 0.2.0 (no label)

# Show current version
python scripts/bump_version.py --current

# Skip git operations (for testing)
python scripts/bump_version.py patch --no-git
```

## Version Files

The bump script updates these files:
- `frontend/app/version.ts` - TypeScript version module
- `frontend/package.json` - npm package version
- `pyproject.toml` - Python package version

## Workflow

### 1. Development in Feature Branch

```bash
git checkout -b feature/my-feature
# Make changes and commit
git add .
git commit -m "Add new feature"
```

### 2. Bump Version After PR Merge

After your PR is merged to `main`:

```bash
git checkout main
git pull origin main

# Bump version (choose appropriate bump type)
python scripts/bump_version.py patch  # or minor/major

# Push commit and tag
git push origin main
git push origin v0.1.5-beta  # replace with actual version
```

### 3. Automatic GitHub Release

When you push a version tag (e.g., `v0.1.5-beta`), GitHub Actions automatically:
1. Creates a GitHub Release
2. Generates changelog from commits
3. Marks pre-release appropriately (alpha, beta, rc)

## Version Display

The version is displayed in the frontend footer.

## Pre-release Guidelines

- **Alpha**: Active development, expect changes
- **Beta**: Feature freeze, bug fixing (current stage)
- **RC**: Release candidate, final testing
- **Stable** (no label): Production ready

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 0.2.0-beta | 2025-12-03 | HED annotations integration (human + LLM), compact UI layout |
| 0.1.4-beta | 2025-11-27 | Add semantic versioning, Cloudflare deployment |
| 0.1.0 | 2025-11-24 | Initial release |
