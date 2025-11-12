# Contributing to Pulse AI Studio

Thank you for considering contributing to Pulse AI Studio!

## Development Setup

1. **Prerequisites**
   - Node.js 18+
   - Python 3.11+
   - pnpm 8+
   - Docker & Docker Compose

2. **Clone and Install**
   ```bash
   git clone https://github.com/Samer-Is/pulse.git
   cd pulse
   pnpm install
   ```

3. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your local values
   ```

## Development Workflow

### Running Locally

```bash
# Start all services with Docker
make docker-up

# Or run individually:
cd apps/web && pnpm dev      # Frontend on :3000
cd apps/api && uvicorn ...   # API on :8000
cd apps/workers && pnpm dev  # Workers
```

### Code Style

We enforce strict code quality standards:

- **TypeScript/JavaScript**: ESLint + Prettier
- **Python**: Ruff + Black
- **Commits**: Conventional Commits format

Pre-commit hooks will automatically run linters.

### Commit Message Format

```
<type>(<scope>): <subject>

Types: feat, fix, docs, style, refactor, perf, test, chore, build, ci
```

Examples:
```
feat(chat): add streaming support for OpenAI
fix(api): handle rate limit errors gracefully
docs(readme): update local dev setup instructions
```

### Testing

```bash
# TypeScript tests
pnpm test

# Python tests
cd apps/api && pytest
```

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feat/my-feature
   ```

2. **Make your changes**
   - Write tests for new features
   - Update documentation
   - Follow code style guidelines

3. **Commit using conventional commits**
   ```bash
   git commit -m "feat(scope): description"
   ```

4. **Push and create PR**
   ```bash
   git push origin feat/my-feature
   ```

5. **PR Requirements**
   - All CI checks must pass
   - Code review approved
   - Up-to-date with main branch

## Project Structure

```
pulse/
├── apps/
│   ├── web/       # Next.js frontend
│   ├── api/       # FastAPI backend
│   └── workers/   # Async job workers
├── packages/
│   └── shared/    # Shared types & utils
├── infra/
│   └── terraform/ # Infrastructure as Code
└── docs/          # Documentation
```

## Architecture Guidelines

- **Frontend**: React Server Components, TypeScript strict mode
- **Backend**: FastAPI, type hints, async/await
- **Database**: PostgreSQL via SQLAlchemy, Alembic migrations
- **Infrastructure**: AWS-only, managed via Terraform
- **Security**: All secrets in AWS Secrets Manager, never in code

## Adding New Features

### New AI Provider

1. Create provider file in `apps/api/app/providers/`
2. Implement standard interface
3. Add provider config to shared types
4. Update frontend model picker
5. Add tests

### New Feature (CV/Slide/etc)

1. Add database schema (Alembic migration)
2. Create API endpoints
3. Implement business logic
4. Add frontend page/component
5. Update quota enforcement
6. Add tests

## Documentation

Update these files when making significant changes:

- `docs/ACTIVITY.md` - Log your changes
- `README.md` - Update if setup changes
- `build_checklist.json` - Track progress

## Getting Help

- Open an issue for bugs or feature requests
- Check existing issues before creating new ones
- Be respectful and constructive

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

