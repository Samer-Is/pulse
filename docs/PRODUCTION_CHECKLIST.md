# 🚀 Production Readiness Checklist

Use this checklist before deploying Pulse AI Studio to production.

## ✅ Infrastructure

- [ ] **AWS Account configured** with programmatic access
- [ ] **Terraform state backend** configured (S3 + DynamoDB for locking)
- [ ] **VPC and networking** deployed via Terraform
- [ ] **EC2 instances** provisioned with appropriate instance types
- [ ] **RDS PostgreSQL** deployed with:
  - [ ] Automated backups enabled
  - [ ] Multi-AZ deployment (recommended for production)
  - [ ] Encryption at rest enabled
  - [ ] SSL/TLS connections enforced
- [ ] **S3 bucket** created with:
  - [ ] Versioning enabled
  - [ ] Lifecycle policies configured
  - [ ] Public access blocked
- [ ] **SQS queue** configured with:
  - [ ] Dead Letter Queue (DLQ) for failed jobs
  - [ ] Message retention period set
- [ ] **ECR repositories** created for Docker images
- [ ] **Secrets Manager** configured with all API keys
- [ ] **Security Groups** properly configured:
  - [ ] RDS accessible only from EC2
  - [ ] EC2 HTTPS/HTTP from internet
  - [ ] Minimal open ports

## 🔐 Security

- [ ] **Environment variables** never committed to Git
- [ ] **AWS Secrets Manager** storing all sensitive data
- [ ] **JWT secret** is strong and unique (32+ characters)
- [ ] **Database passwords** are strong and rotated
- [ ] **Google OAuth** configured with:
  - [ ] Prod redirect URIs
  - [ ] Scopes limited to required permissions
- [ ] **Stripe webhooks** configured with signature verification
- [ ] **CORS** configured with specific allowed origins
- [ ] **Rate limiting** enabled and tested
- [ ] **Security headers** configured (CSP, HSTS, X-Frame-Options)
- [ ] **HTTPS** enforced with valid SSL certificate
- [ ] **SSH keys** for EC2 access stored securely
- [ ] **IAM roles** follow least-privilege principle
- [ ] **Input validation** on all API endpoints
- [ ] **SQL injection** prevention (parameterized queries)
- [ ] **XSS protection** enabled

## 📊 Monitoring & Logging

- [ ] **Structured JSON logging** configured
- [ ] **Log levels** appropriate for production (INFO)
- [ ] **CloudWatch Logs** streaming from containers (optional)
- [ ] **Health check endpoints** functional:
  - [ ] `/health`
  - [ ] `/health/ready`
  - [ ] `/health/live`
- [ ] **Uptime monitoring** configured (e.g., UptimeRobot, Pingdom)
- [ ] **Error tracking** setup (e.g., Sentry) (optional)
- [ ] **CloudWatch Alarms** for:
  - [ ] API error rate > 5%
  - [ ] EC2 CPU > 80%
  - [ ] RDS connections > 80%
  - [ ] SQS DLQ message count > 0
- [ ] **Metrics dashboard** for usage tracking

## 🗃️ Database

- [ ] **Database migrations** run successfully
- [ ] **Connection pooling** configured
- [ ] **Indexes** created for frequently queried columns
- [ ] **Backup strategy** defined and tested:
  - [ ] RDS automated backups configured
  - [ ] Backup retention period set (7+ days)
  - [ ] Manual backup tested
  - [ ] Restore procedure documented and tested
- [ ] **Database performance** tested under load
- [ ] **Query optimization** for slow queries

## 🐳 Docker & Deployment

- [ ] **Docker images** built and tested
- [ ] **Multi-stage builds** used for optimized image size
- [ ] **Images tagged** with version numbers
- [ ] **ECR authentication** working
- [ ] **Docker Compose prod** file configured
- [ ] **Container health checks** defined
- [ ] **Restart policies** set (`unless-stopped`)
- [ ] **Log rotation** configured to prevent disk fill
- [ ] **Resource limits** set (CPU, memory)

## 🧪 Testing

- [ ] **Unit tests** passing for critical functions
- [ ] **Integration tests** for API endpoints
- [ ] **End-to-end tests** for critical user flows
- [ ] **Load testing** performed:
  - [ ] API can handle expected traffic
  - [ ] Database performs under load
  - [ ] Workers process jobs efficiently
- [ ] **Security testing**:
  - [ ] OWASP Top 10 vulnerabilities checked
  - [ ] Dependency vulnerabilities scanned
- [ ] **Browser testing** across:
  - [ ] Chrome
  - [ ] Firefox
  - [ ] Safari
  - [ ] Edge

## 💳 Payments (Stripe)

- [ ] **Stripe account** in live mode
- [ ] **Live API keys** stored in Secrets Manager
- [ ] **Webhook endpoint** configured:
  - [ ] URL points to production API
  - [ ] Signature verification enabled
  - [ ] All required events selected
- [ ] **Stripe products** and prices created:
  - [ ] Starter plan
  - [ ] Plus plan
  - [ ] Pro plan
- [ ] **Customer portal** tested
- [ ] **Subscription lifecycle** tested:
  - [ ] Checkout flow
  - [ ] Subscription activation
  - [ ] Plan upgrade/downgrade
  - [ ] Cancellation
- [ ] **Test payment** completed successfully

## 🤖 AI Provider APIs

- [ ] **OpenAI API key** valid and funded
- [ ] **Anthropic API key** valid and funded
- [ ] **Google Vertex AI** project configured:
  - [ ] Service account created
  - [ ] Vertex AI API enabled
  - [ ] Imagen API enabled
  - [ ] Quotas sufficient
- [ ] **API error handling** tested for all providers
- [ ] **Rate limiting** respected for each provider
- [ ] **Fallback logic** for provider failures

## 📱 Frontend

- [ ] **Production build** working (`pnpm build`)
- [ ] **Environment variables** configured
- [ ] **API base URL** pointing to production
- [ ] **Google OAuth** redirect URIs updated
- [ ] **Performance optimization**:
  - [ ] Code splitting enabled
  - [ ] Images optimized
  - [ ] Bundle size analyzed
- [ ] **SEO basics**:
  - [ ] Meta tags configured
  - [ ] sitemap.xml generated
  - [ ] robots.txt configured
- [ ] **Analytics** integrated (optional)
- [ ] **Error boundaries** catching React errors

## 🔄 CI/CD

- [ ] **GitHub Actions** workflows configured
- [ ] **Secrets** added to GitHub repository:
  - [ ] AWS credentials
  - [ ] EC2 SSH key
- [ ] **Automated tests** run on every push
- [ ] **Linting and formatting** enforced
- [ ] **Docker build** automated
- [ ] **ECR push** automated
- [ ] **Deployment trigger** on tag push tested

## 🌐 Domain & DNS

- [ ] **Domain name** purchased and configured
- [ ] **DNS records** pointing to EC2/ALB:
  - [ ] A record for main domain
  - [ ] A record for API subdomain (if separate)
- [ ] **SSL/TLS certificate** obtained and configured:
  - [ ] Let's Encrypt or AWS Certificate Manager
  - [ ] Auto-renewal configured
  - [ ] Certificate valid for all subdomains
- [ ] **HTTPS redirect** from HTTP enforced

## 📧 Email (Optional)

- [ ] **Transactional email service** configured:
  - [ ] AWS SES, SendGrid, or Mailgun
  - [ ] Domain verified
  - [ ] SPF and DKIM records added
- [ ] **Email templates** created:
  - [ ] Welcome email
  - [ ] Password reset
  - [ ] Subscription confirmation
  - [ ] Invoice receipt

## 📖 Documentation

- [ ] **README.md** up to date with:
  - [ ] Architecture diagram
  - [ ] Setup instructions
  - [ ] API documentation links
- [ ] **DEPLOYMENT.md** complete
- [ ] **API documentation** (Swagger/ReDoc) accessible
- [ ] **Admin guide** for user management
- [ ] **Troubleshooting guide** for common issues
- [ ] **Runbook** for incidents

## 💰 Costs & Billing

- [ ] **AWS billing alerts** configured
- [ ] **Cost estimates** calculated for expected usage
- [ ] **Reserved Instances** considered for cost savings
- [ ] **S3 lifecycle policies** to manage storage costs
- [ ] **CloudWatch Logs retention** set appropriately

## 🚨 Disaster Recovery

- [ ] **Backup strategy** documented
- [ ] **Recovery procedures** tested
- [ ] **Database backup** tested and working
- [ ] **S3 cross-region replication** configured (optional)
- [ ] **Incident response plan** documented
- [ ] **On-call rotation** defined (if applicable)

## ⚖️ Legal & Compliance

- [ ] **Privacy Policy** published
- [ ] **Terms of Service** published
- [ ] **Cookie notice** displayed (if using cookies)
- [ ] **GDPR compliance** if serving EU users:
  - [ ] Data processing agreement
  - [ ] Right to deletion implemented
  - [ ] Data export functionality
- [ ] **PCI DSS** compliance (Stripe handles card data)

## 🎯 Post-Launch

- [ ] **Smoke tests** run on production
- [ ] **User acceptance testing** completed
- [ ] **Performance baseline** established
- [ ] **Monitoring dashboards** reviewed
- [ ] **Error rates** acceptable
- [ ] **Response times** meet SLA
- [ ] **Team notified** of go-live
- [ ] **Documentation** shared with team
- [ ] **Support channels** ready

---

## Sign-Off

- [ ] **Dev Team Lead**: _________________ Date: _______
- [ ] **DevOps/Platform**: _________________ Date: _______
- [ ] **Security Review**: _________________ Date: _______
- [ ] **Product Owner**: _________________ Date: _______

---

**Notes**: This checklist should be reviewed and updated regularly as the project evolves.

