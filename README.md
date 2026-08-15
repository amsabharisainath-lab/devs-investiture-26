# DEVS Investiture

This readme deals with basic rules and instructions of the codebase.

## Client/

The React frontend codebase is located inside the `client/` folder. Any frontend updates must be done there.

## Server/

The backend codebase is situated inside the `server/` folder. Set up and operate a FastAPI project in that directory for all backend updates.

## Git commit conventions (required)

Follow conventional commit-style types for all commits. The commit type can be one of:

- `feat`: Commits which add a new feature.
- `fix`: Commits that fix a bug.
- `refactor`: Commits that rewrite or restructure code without changing behavior.
- `perf`: Commits that improve performance.
- `style`: Commits that do not affect code behavior (formatting, whitespace, semicolons, etc.).
- `test`: Commits that add or correct tests.
- `docs`: Commits that affect documentation only.
- `build`: Commits that affect build system, CI, dependencies, or project version.
- `ops`: Commits that affect operational components (infrastructure, deployment, backups, recovery).
- `chore`: Miscellaneous commits (e.g., modifying .gitignore, small maintenance tasks).

Use concise, descriptive commit messages following this pattern:

<type>(scope?): short description

Examples (dependency updates — MUST be separate commits):

- Backend dependency update (Django/requirements):

  chore: added django-rest-framework to requirements.txt

- Frontend dependency update (npm/package.json):

  chore: added @tanstack/react-query to package.json and updated package-lock.json

Notes and rules (enforced):

- Any dependency change — whether backend or frontend — must be committed in its own dedicated `chore:` commit. Do not bundle dependency changes with feature or bugfix commits.
- For package changes, include where the change was made (e.g., `requirements.txt`, `package.json`, `pyproject.toml`).
- If the dependency update requires code changes (e.g., API changes), those changes must be in a separate follow-up commit with an appropriate type (e.g., `feat:` or `fix:`), referencing the dependency-chore commit.

