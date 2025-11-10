# Security Policy

## Supported Versions

Currently supporting:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please:

1. **DO NOT** open a public GitHub issue
2. Email security details to your designated security contact
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Security Measures

### Infrastructure
- All services run in private subnets (except ALB)
- Security groups restrict traffic to minimum required
- Secrets stored in AWS Secrets Manager (never in code)
- TLS/HTTPS enforced for all external connections
- CloudWatch logs and X-Ray tracing enabled

### Application
- JWT tokens with httpOnly cookies
- CSRF protection enabled
- Input validation on all endpoints
- SQL injection prevention via SQLAlchemy ORM
- Content moderation hooks for user-generated content
- Rate limiting per user (60 req/60s)

### Data
- Database credentials rotated via Secrets Manager
- S3 buckets private with presigned URLs (time-limited)
- No PII stored in logs
- User data encrypted at rest (Aurora + S3)

### Dependencies
- Regular dependency updates
- Automated vulnerability scanning (Dependabot recommended)
- Pin exact versions in lock files

## Best Practices for Contributors

1. Never commit secrets or credentials
2. Use environment variables for configuration
3. Validate and sanitize all user inputs
4. Follow principle of least privilege for IAM roles
5. Use prepared statements for SQL queries
6. Keep dependencies updated
7. Run security linters before submitting PRs

## Incident Response

In case of a security incident:
1. Immediately revoke compromised credentials via AWS Secrets Manager
2. Review CloudWatch logs and X-Ray traces
3. Rotate all secrets as precaution
4. Apply patches and redeploy via CI/CD
5. Document incident in private security log
6. Notify affected users if data breach occurred

## Compliance

- Payment handling via PCI-compliant providers (HyperPay)
- GDPR considerations for user data (export/deletion endpoints planned)
- Data retention policies configurable per deployment

## Security Contacts

- Primary: [To be defined]
- Backup: [To be defined]

**Response SLA:** We aim to acknowledge security reports within 48 hours and provide updates every 72 hours until resolved.
