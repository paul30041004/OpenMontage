---
name: security-review
description: Use this skill when adding authentication, handling user input, working with secrets, creating API endpoints, or implementing payment/sensitive features. Provides comprehensive security checklist and patterns.
metadata:
  origin: ECC
---

# Security Review Skill

This skill ensures all code follows security best practices and identifies potential vulnerabilities.

## When to Activate

- Implementing authentication or authorization
- Handling user input or file uploads
- Creating new API endpoints
- Working with secrets or credentials
- Storing or transmitting sensitive data
- Integrating third-party APIs

## Security Checklist

### 1. Secrets Management
- No hardcoded API keys, tokens, or passwords
- All secrets in environment variables (`.env`)
- `.env` and `.env.local` in `.gitignore`
- No secrets in git history or commit diffs
- Verify pre-push security hooks are active

### 2. Input Validation
- Validate all user inputs with schemas (e.g. Zod, Pydantic)
- Enforce strict size and MIME type checks on file uploads
- Reject unexpected keys or unvalidated payload fields

### 3. Injection Prevention
- All database queries must use parameterized queries
- No string concatenation in SQL queries
- Sanitize HTML to prevent Cross-Site Scripting (XSS)
- Configure strict Content Security Policy (CSP) headers

### 4. Logging & Error Safety
- Never log passwords, tokens, full request bodies, or secret keys
- Generic error messages for end users
- Never expose internal stack traces or database schema details to clients
