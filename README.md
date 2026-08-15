# DEVS Investiture --- Event Registration & Attendance Platform

A focused, secure event platform for the DEVS Investiture ceremony at
Rajalakshmi Engineering College.

> **Delivery target:** 10 development days + 1 dedicated
> production/DevOps day\
> **Design:** Black and white, Vercel-inspired, fast and
> information-dense

## Table of Contents

-   [Product Overview](#product-overview)
-   [User Roles & Permissions](#user-roles--permissions)
-   [Core Workflows](#core-workflows)
-   [Technology Stack](#technology-stack)
-   [Repository Responsibilities](#repository-responsibilities)
-   [Architecture Principles](#architecture-principles)
-   [Authentication & Authorization](#authentication--authorization)
-   [QR Ticket & Attendance](#qr-ticket--attendance)
-   [Admin & Checker Console](#admin--checker-console)
-   [OD PDF Generation](#od-pdf-generation)
-   [Design System](#design-system)
-   [Code Quality](#code-quality)
-   [GitHub Workflow](#github-workflow)
-   [Security Requirements](#security-requirements)
-   [Performance & Reliability](#performance--reliability)
-   [Docker & VPS Deployment](#docker--vps-deployment)
-   [10 + 1 Day Sprint](#10--1-day-sprint)
-   [Definition of Done](#definition-of-done)
-   [Key Risks](#key-risks)
-   [Future Reusability](#future-reusability)
-   [Work Assigned](#work-assigned)

------------------------------------------------------------------------

## Product Overview

Build a fast, secure, college-restricted event platform where
Rajalakshmi Engineering College students authenticate with Google using
their institutional `@rajalakshmi.edu.in` account, register exactly once
for the DEVS Investiture, receive a QR ticket, and are verified at entry
by authenticated checker/admin teams.

### Core outcomes

-   Google-only institutional authentication.
-   One registration per student, enforced server-side and at database
    level.
-   Immediate entry QR generation and institutional-email delivery.
-   Opaque, short-lived, one-time QR credentials with no PII in the QR.
-   Multiple checker stations operating concurrently.
-   Manual physical ID-card verification after QR validation.
-   `Present`, `Absent`, and `Forgery` attendance decisions.
-   Controlled on-spot registration.
-   Exit QR locked until the configured exit window, with Super Admin
    bulk dispatch.
-   Watermarked OD PDF generation.
-   Auditable operational actions.
-   Dockerized VPS deployment.

### Scope

**Student:** login, registration, own ticket, email ticket, exit QR when
enabled, own OD/registration status.

**Checker/Admin:** QR scanning, student lookup, filters, identity
verification, attendance decisions, operational dashboard and exception
handling.

**Super Admin:** all admin capabilities plus role/station assignment,
event configuration, bulk exit dispatch, audit review and exports.

### Non-goals for the MVP

-   Password authentication.
-   General college ERP functionality.
-   Kubernetes or unnecessary orchestration.
-   Premature microservices.
-   Cryptographic OD signing/DSC/eSign.
-   Redis unless measured traffic justifies it.
-   Non-essential UI features.

------------------------------------------------------------------------

## User Roles & Permissions

  Capability                       Student   Checker/Admin   Super Admin
  ------------------------------- --------- --------------- -------------
  Google institutional login         Yes          Yes            Yes
  Register self                      Yes          No             No
  View own ticket                    Yes          No             No
  Scan QR                            No           Yes            Yes
  Search/filter registered list      No           Yes            Yes
  Mark Present/Absent/Forgery        No           Yes            Yes
  On-spot registration               No       Controlled         Yes
  Bulk exit dispatch                 No           No             Yes
  Event configuration                No           No             Yes
  Station assignment                 No         Limited          Yes
  Audit/export                       No         Limited          Yes

Role assignment is always enforced server-side. Frontend role state is
never a security boundary.

------------------------------------------------------------------------

## Core Workflows

### Student Registration

1.  Student selects **Continue with Google**.
2.  Backend verifies Google identity, verified email and
    `@rajalakshmi.edu.in`.
3.  Local identity is created/retrieved using Google's stable `sub`.
4.  Backend checks the event/student uniqueness constraint.
5.  Student completes the required registration data.
6.  Registration transaction commits.
7.  Entry QR is generated.
8.  QR is shown immediately.
9.  Registration confirmation and ticket are sent asynchronously to the
    institutional email.

### Entry Verification

1.  Checker signs into an assigned scanner station.
2.  Camera scans the opaque QR.
3.  Backend atomically validates event, action, expiry, registration and
    token-consumption state.
4.  Registered student details are returned.
5.  Checker compares those details with the physical college ID card.
6.  Checker records `Present`, `Absent` or `Forgery`.
7.  Actor, station and server timestamp are recorded.
8.  Duplicate, expired and invalid credentials go to the exception path.

### Exit Workflow

1.  Exit action remains locked before the configured window.
2.  Super Admin opens the exit window.
3.  Exit access can be bulk-dispatched to registered students.
4.  Student opens the exit ticket and submits the QR through the exit
    scan action.
5.  Backend validates and consumes the exit credential.
6.  Exit timestamp is recorded.
7.  Unmatched/suspicious cases remain visible to admins.

### On-Spot Registration

On-spot registration uses the same institutional identity and uniqueness
rules as normal registration. It requires an authenticated admin session
and is fully audited.

### OD Workflow

Generate the OD PDF from trusted server-side registration data, apply a
repeated student-name and roll-number watermark around/below the
content, record document metadata and SHA-256, protect the file from
public access, and send it to eligible students after the relevant
QR/attendance condition is satisfied.

The MVP does **not** implement cryptographic digital signing.

------------------------------------------------------------------------

## Technology Stack

### Frontend

  Technology            Purpose
  --------------------- -----------------------------------
  React                 UI framework
  Vite                  Build/development tooling
  TypeScript            Strict type safety
  shadcn/ui             Shared UI primitives
  Tailwind CSS          Styling/design tokens
  TanStack Query        Server-state caching/invalidation
  Zustand               Client-state management
  QR scanning library   Camera-based scanning
  Typed API client      Backend communication

Frontend rules:

-   Use strict TypeScript.
-   Use feature-oriented organization.
-   Use shadcn/ui rather than repeatedly building primitive controls.
-   Use TanStack Query for server state.
-   Use Zustand only for genuine client state.
-   Avoid excessive `useState`/`useEffect`.
-   Keep transient scanner state local.
-   Never treat route guards as authorization.
-   Preserve accessibility.

### Backend

  Technology                Purpose
  ------------------------- -----------------------------
  Python                    Backend language
  FastAPI                   HTTP API framework
  Pydantic                  API validation
  SQLAlchemy                ORM/database access
  Alembic                   Database migrations
  PostgreSQL                Primary relational database
  Google OAuth/OIDC         Authentication
  Secure HttpOnly cookies   Browser sessions
  Background worker/tasks   Email/PDF operations
  PDF generation library    OD PDF generation
  SMTP/email provider       Email delivery
  SHA-256                   Document integrity

FastAPI backend layers:

1.  **API/Router** --- HTTP concerns, dependencies, response mapping.
2.  **Application/Service** --- use-case orchestration.
3.  **Domain** --- entities, enums, business rules and invariants.
4.  **Repository/Data Access** --- SQLAlchemy queries and persistence.
5.  **Infrastructure** --- Google, email, PDF, storage and external
    integrations.

Backend rules:

-   Explicit transaction boundaries.
-   No hidden commits inside repositories.
-   Pydantic at API boundaries.
-   Never expose ORM objects directly.
-   Dependency injection for sessions, users, roles and services.
-   Structured logging with request/trace IDs.
-   Never log tokens, cookies, Google credentials or unnecessary PII.
-   Lint, format, type-check and test before merge.

### Infrastructure

  Technology            Purpose                                  Required
  --------------------- --------------------------------------- ----------
  Docker                Containerization                           Yes
  Docker Compose        Initial VPS orchestration                  Yes
  HTTPS reverse proxy   TLS, routing, headers, request limits      Yes
  PostgreSQL            Database                                   Yes
  Redis                 Cache/rate-limit support                 Optional
  Firewall              VPS protection                             Yes
  SMTP/email provider   Email delivery                             Yes
  DNS                   Event domain/subdomain                     Yes
  Backup storage        Database recovery                          Yes

------------------------------------------------------------------------

## Repository Responsibilities

### Client/

The React frontend codebase is located inside the `client/` folder. Any
frontend updates must be done there.

### Server/

The backend codebase is situated inside the `server/` folder. Set up and
operate a FastAPI project in that directory for all backend updates.

------------------------------------------------------------------------

## Architecture Principles

The browser is a thin client. The backend is authoritative for identity,
permissions, registration, QR validity, attendance and event timing.
PostgreSQL is authoritative for concurrent mutations.

Never use frontend state, cached lists, frontend counters or in-memory
backend flags as the source of truth for registration uniqueness, QR
consumption or attendance.

Every attendance mutation must be protected by a database transaction.

### Core data concepts

  Entity         Important constraints
  -------------- -----------------------------------------------------
  User           Unique Google `sub`; normalized institutional email
  Event          Single active DEVS Investiture event
  Registration   `UNIQUE(event_id, user_id)`
  QRToken        Opaque random token hash; one-time consumption
  Attendance     One current attendance record per registration
  ScanEvent      Append-only scan history
  Station        Identifies scanner lane/device
  ODDocument     Protected file + SHA-256 metadata
  AuditEvent     Append-only operational history

------------------------------------------------------------------------

## Authentication & Authorization

Google OAuth/OIDC is the **only authentication method**.

Accepted domain:

``` text
@rajalakshmi.edu.in
```

The backend must reject non-institutional identities even if a user
calls an API directly.

Use Google's stable `sub` as the external identity key. Email is an
attribute, not the sole identity key.

After backend verification, create a local application session using:

-   `Secure`
-   `HttpOnly`
-   Appropriate `SameSite`
-   No long-lived auth tokens in `localStorage`

Authorization is server-side. Students cannot access scanner/admin APIs
or mutate attendance. Checker/Admin users cannot change protected event
rules unless elevated. Super Admin has elevated capabilities.

------------------------------------------------------------------------

## QR Ticket & Attendance

The QR is a **credential, not the attendance record**.

### QR requirements

-   Cryptographically random.
-   Opaque.
-   No PII.
-   Tied to event/registration.
-   Short-lived.
-   Server-side hash storage.
-   One-time consumption.
-   Server time for validation.
-   Explicit `ENTRY`/`EXIT` action.

Recommended entry validity is **5 minutes**, extendable to 10 minutes
only if rehearsal/network conditions justify it.

### QR lifecycle

  --------------------------------------------------------------------------------------------------
  Stage                   Backend action                                 Rule
  ----------------------- ---------------------------------------------- ---------------------------
  Issue                   Generate random token                          No PII

  Store                   Store token hash                               Protect credential

  Display                 Render QR                                      Credential only

  Scan                    Send token to API                              Authenticated checker

  Validate                Check                                          Server time
                          event/action/expiry/registration/consumption   

  Verify                  Return student details                         Physical ID comparison

  Commit                  Consume token + attendance mutation atomically Prevent replay

  Audit                   Record ScanEvent                               Actor/station/result/time
  --------------------------------------------------------------------------------------------------

### Race-condition handling

Two admins scanning the same QR at nearly the same time must not both
succeed.

Use one atomic transaction for token validation, token consumption and
attendance mutation.

A suitable approach is a conditional update such as:

``` sql
UPDATE qr_tokens
SET consumed_at = CURRENT_TIMESTAMP
WHERE id = :token_id
  AND consumed_at IS NULL
  AND expires_at > CURRENT_TIMESTAMP;
```

Check the affected-row count. Exactly one scanner wins. The loser
receives a deterministic `already consumed`/`already verified` response.

Registration uses the same principle through:

``` text
UNIQUE(event_id, user_id)
```

Never rely on client-side button disabling.

### Attendance states

  State         Meaning
  ------------- --------------------------------------------
  `PRESENT`     Valid QR and physical ID match
  `ABSENT`      Registered but no valid entry verification
  `FORGERY`     QR/identity mismatch
  `DUPLICATE`   Credential already consumed
  `EXPIRED`     Credential outside validity window
  `INVALID`     Wrong/malformed/unknown credential

------------------------------------------------------------------------

## Admin & Checker Console

The scanner UI is camera-first and optimized for phones/tablets.

Show immediately after a valid scan:

-   Student name
-   Roll number
-   Department
-   Year
-   Registration status
-   Previous attendance state
-   ID-card verification prompt
-   Station identity

Admin list requirements:

-   Pagination
-   Server-side search
-   Name search
-   Roll-number search
-   Year
-   Department
-   Registration status
-   Entry status
-   Exit status
-   Verification outcome
-   Forgery filter

Dashboard counts:

-   Registered
-   Present
-   Absent/unverified
-   Forgery
-   Entered
-   Exited
-   Unresolved exceptions

Every scan records actor, station, registration, token, action, result
and server receipt time.

------------------------------------------------------------------------

## OD PDF Generation

The MVP generates a digitally produced **watermarked PDF** and does not
implement cryptographic signing.

Requirements:

-   Generate only from trusted server-side data.
-   Watermark student name.
-   Watermark roll number.
-   Repeat watermark around/below the content.
-   Do not obscure primary content.
-   Record document ID, registration ID, timestamp and SHA-256.
-   Store outside public static web root.
-   Serve through authorized endpoints only.
-   Send automatically to eligible students after the relevant
    QR/attendance condition.

Do not call the watermark a digital signature.

------------------------------------------------------------------------

## Design System

### Visual direction

Black and white, Vercel-inspired, high contrast, minimal and
information-dense.

  Token         Direction
  ------------- -----------------------
  Background    `#FFFFFF`, `#FAFAFA`
  Foreground    `#000000`, `#111111`
  Muted         `#666666`, `#A1A1AA`
  Border        `#E5E5E5`
  Primary       Black
  Destructive   Black + icon/text
  Radius        Small/moderate
  Typography    Inter/Geist-like sans

Do not introduce a rainbow palette.

### shadcn/ui

Use shadcn/ui as the shared UI primitive layer.

Preferred components:

`Button`, `Input`, `Label`, `Card`, `Dialog`, `AlertDialog`, `Badge`,
`Tabs`, `DropdownMenu`, `Table`, `Pagination`, `Select`, `Sheet`,
`Skeleton`, `Toast/Toaster`.

Build scanner-specific components on top:

-   `QRScanner`
-   `ScanResultCard`
-   `IdentityCheckPanel`
-   `AttendanceStatusBadge`
-   `StationHeader`

Accessibility and focus behavior must not be removed for visual
minimalism.

### UX

Student:

``` text
Google Login → Registration → Ticket
```

Checker:

``` text
Scan → Verify Identity → Decision → Next Student
```

Admin:

``` text
Search → Filter → Inspect → Act → Monitor
```

------------------------------------------------------------------------

## Code Quality

### Frontend

-   Strict TypeScript.
-   Reusable components.
-   Typed API contracts.
-   TanStack Query for server state.
-   Zustand for required client state.
-   No duplicated API logic.
-   No security decisions based only on frontend state.
-   Accessible controls.
-   Clear loading/error/empty states.
-   Avoid giant components and unnecessary effects.

### Backend

-   Routers contain HTTP concerns only.
-   Services contain application use cases.
-   Domain rules remain explicit.
-   Repositories manage persistence.
-   Infrastructure handles external integrations.
-   Explicit transactions.
-   Pydantic API boundaries.
-   No direct ORM exposure.
-   Dependency injection.
-   Structured logs.
-   No sensitive credentials/tokens in logs.
-   Automated tests for business-critical paths.

### Documentation

Meaningful features should include:

-   Clear naming.
-   Useful comments only for non-obvious reasoning.
-   Updated API documentation.
-   Tests.
-   Clear PR description.
-   Clear commit history.

Avoid giant functions, duplicated business rules, magic values, silent
exception handling and dead code.

------------------------------------------------------------------------

## GitHub Workflow

The repository follows:

``` text
Fork
  ↓
Create feature branch
  ↓
Implement
  ↓
Test
  ↓
Commit
  ↓
Push to fork
  ↓
Open PR
  ↓
Review
  ↓
Address feedback
  ↓
Approval
  ↓
Lead merges
```

### Branch & fork rules

1.  Fork the repository.
2.  Clone your fork.
3.  Add upstream.
4.  Create a dedicated branch.
5.  Implement only the assigned task.
6.  Test locally.
7.  Push to your fork.
8.  Raise a PR against upstream.
9.  Address review feedback.
10. Leads merge the PR.

**Do not directly push feature work to the upstream/main branch.**

### Pull Requests

Every PR should explain:

-   What changed.
-   Why it changed.
-   Requirement/task addressed.
-   Testing performed.
-   Database changes.
-   Dependency changes.
-   Deployment implications.
-   UI screenshots/video when appropriate.

PR checklist:

-   [ ] Scope is limited.
-   [ ] Tests updated.
-   [ ] No secrets committed.
-   [ ] No unrelated files changed.
-   [ ] Dependency rules followed.
-   [ ] Documentation updated if needed.
-   [ ] Security impact considered.
-   [ ] PR description is complete.
-   [ ] Reviewer can reproduce/test the change.

------------------------------------------------------------------------

## Git Commit Conventions

Follow conventional commit-style types for all commits.

The commit type can be one of:

-   `feat`: Commits which add a new feature.
-   `fix`: Commits that fix a bug.
-   `refactor`: Commits that rewrite or restructure code without
    changing behavior.
-   `perf`: Commits that improve performance.
-   `style`: Commits that do not affect code behavior (formatting,
    whitespace, semicolons, etc.).
-   `test`: Commits that add or correct tests.
-   `docs`: Commits that affect documentation only.
-   `build`: Commits that affect build system, CI, dependencies, or
    project version.
-   `ops`: Commits that affect operational components (infrastructure,
    deployment, backups, recovery).
-   `chore`: Miscellaneous commits (e.g., modifying `.gitignore`, small
    maintenance tasks).

Use concise, descriptive commit messages following:

``` text
(scope?): short description
```

Examples:

``` text
feat(auth): add Google institutional login
fix(attendance): prevent duplicate QR consumption
refactor(registration): separate registration service
perf(admin): optimize attendance query
style(client): format scanner components
test(attendance): add concurrent scan test
docs(readme): document GitHub workflow
build(client): update build configuration
ops(vps): add production backup script
chore: update gitignore
```

### Dependency changes --- required rule

**Any dependency change, whether backend or frontend, must be committed
in its own dedicated `chore:` commit.**

Do not bundle dependency changes with feature or bug-fix commits.

Backend example:

``` text
chore: added django-rest-framework to requirements.txt
```

Frontend example:

``` text
chore: added @tanstack/react-query to package.json and updated package-lock.json
```

For this project, dependency changes may occur in:

-   `requirements.txt`
-   `pyproject.toml`
-   `package.json`
-   `package-lock.json`

For package changes, include where the change was made.

If a dependency update requires code changes, those code changes must be
a separate follow-up commit with the appropriate type, such as `feat:`
or `fix:`, referencing the dependency-chore commit.

Example:

``` text
chore: add sqlalchemy dependency to requirements.txt
```

followed by:

``` text
feat(database): add SQLAlchemy registration repository
```

Make as many meaningful commits as necessary for proper version control
and traceability. Avoid one giant commit for an entire feature.

------------------------------------------------------------------------

## Security Requirements

Security is a release requirement.

  --------------------------------------------------------------------------
  Threat                  Control                    Acceptance
  ----------------------- -------------------------- -----------------------
  XSS                     React escaping, output     Payload never executes
                          encoding, CSP, no unsafe   
                          HTML                       

  SQL injection           SQLAlchemy/parameterized   No query manipulation
                          queries + validation       

  CSRF                    SameSite cookies + CSRF    State-changing
                          strategy                   cross-origin requests
                                                     rejected

  OAuth bypass            Backend Google             No session for invalid
                          verification + domain      identity
                          check                      

  Privilege escalation    Server-side RBAC           Unauthorized APIs
                                                     return `403`

  QR replay/race          Opaque short-lived token + Exactly one concurrent
                          atomic consume             winner

  Brute force/DDoS        Per-IP/user/endpoint rate  Traffic throttled
                          limits                     

  DB burst                Indexes, pagination,       DB remains responsive
                          bounded queries, caching   

  Subdomain exploitation  DNS inventory + no         No dangling service
                          dangling records           record

  Root/admin compromise   Non-root containers +      Recovery path works
                          separate deploy user +     
                          backups                    

  File abuse              MIME/extension/size        Unsafe uploads rejected
                          validation + protected     
                          storage                    

  Secret exposure         Environment/secret storage No credentials in
                                                     repo/image/logs
  --------------------------------------------------------------------------

### Required security tests

Test:

-   XSS payloads in names/search/notes.
-   SQL injection strings across search/filter/input endpoints.
-   Non-institutional OAuth identities.
-   Forged frontend role state.
-   Direct student calls to admin APIs.
-   Same QR from multiple devices concurrently.
-   Expired QR.
-   Already-consumed QR.
-   Registration race.
-   Login/registration/scan request bursts.
-   Oversized/malformed file uploads.
-   DNS records before deployment and retirement.

------------------------------------------------------------------------

## VPS Hardening

-   Expose only HTTPS and required SSH.
-   PostgreSQL and internal services must not be public.
-   Run application containers as non-root where supported.
-   Never mount Docker socket into application containers.
-   Use a separate deploy user.
-   Do not use root for routine deployment.
-   Keep provider/VPS console access as an out-of-band recovery path.
-   Use SSH keys.
-   Disable privileged SSH password login.
-   Maintain firewall rules.
-   Apply security updates where safe.
-   Back up PostgreSQL.
-   Verify an actual restore before the event.
-   Document DNS records.
-   Remove unused/dangling CNAME records.

------------------------------------------------------------------------

## Performance & Reliability

### Frontend caching

Use TanStack Query for:

-   Registered list
-   Attendance list
-   Dashboard
-   Operational views

Invalidate targeted queries after mutations.

### Backend

PostgreSQL is expected to be sufficient for the internal event workload.

Redis is optional and should only be introduced if measured
rate-limit/cache pressure justifies it.

### Indexes

Index:

-   `event_id`
-   `user_id`
-   `roll_no`
-   `department`
-   `year`
-   registration status
-   attendance status
-   `token_hash`

Use pagination and bounded result sizes.

### QR path

Keep the critical path short:

``` text
Authentication
    ↓
Token lookup
    ↓
Database transaction
    ↓
Attendance mutation
    ↓
Response
```

Email/PDF generation must not block QR scanning. Use background
processing.

### Event operations

Use multiple checker stations, reliable Wi-Fi, mobile fallback where
possible, spare devices and a manual exception lane.

Perform a timed rehearsal before production.

------------------------------------------------------------------------

## Docker & VPS Deployment

  Service         Responsibility                          Exposure
  --------------- --------------------------------------- ---------------
  Reverse proxy   TLS, headers, request limits, routing   `80/443`
  Frontend        React/Vite static assets                Internal
  API             FastAPI                                 Internal
  PostgreSQL      Database                                Internal only
  Worker          Email/PDF/background jobs               Internal
  Redis           Optional cache/rate limiting            Internal only

Deployment rules:

-   Docker Compose for initial VPS deployment.
-   Pin production image/dependency versions.
-   Build reproducibly.
-   Keep secrets outside images.
-   Use environment variables/secret mechanisms.
-   Health checks for API/database.
-   Restart policies.
-   Explicit migrations.
-   Verify health before traffic switch.
-   Keep backups independent of container lifecycle.
-   Maintain rollback procedures.

Conceptual deployment:

``` text
Internet
   │
   ▼
HTTPS Reverse Proxy
   │
   ├── Frontend
   │
   └── FastAPI API
          │
          ├── PostgreSQL
          ├── Worker
          └── Optional Redis
```

------------------------------------------------------------------------

## 10 + 1 Day Sprint

Frontend, backend and operational work proceed in parallel.

  -------------------------------------------------------------------------------------------
                    Day Primary Work     Deliverable                         Exit Criterion
  --------------------- ---------------- ----------------------------------- ----------------
                      1 Scope freeze +   Data model, API contract, UI        Frozen MVP
                        architecture +   skeleton, Docker baseline           
                        repo setup                                           

                      2 Google OAuth +   Institutional login, profile,       Eligible student
                        registration     single-registration API             can register

                      3 Ticket/QR +      Entry QR, token service, email      Usable ticket
                        email            ticket                              

                      4 Admin/checker UI Scanner, registered list, filters   Checker can find
                                                                             student

                      5 Entry attendance Atomic scan/consume + attendance    Concurrent scans
                        backend          decisions                           cannot
                                                                             double-accept

                      6 Attendance       Counts, filters, stations,          Multiple
                        dashboard        exceptions                          stations operate

                      7 Exit workflow    Exit lock + exit QR + bulk send     Exit works
                                                                             end-to-end

                      8 OD PDF + on-spot Watermarked PDF + admin             Both flows work
                        registration     registration                        

                      9 Security +       XSS/SQLi/auth/rate-limit/DB-burst   No critical
                        performance      tests                               defects

                     10 Integration +    Event simulation, backups,          Production
                        rehearsal        recovery, fixes                     candidate
                                                                             approved

                     11 Production /     VPS, TLS, DNS, migrations,          Release +
                        DevOps           backup/restore, monitoring          rollback
                                                                             verified
  -------------------------------------------------------------------------------------------

### Scope priority

``` text
Registration / Authentication
        ↓
QR / Attendance Correctness
        ↓
Concurrency / Security
        ↓
Scanner Throughput / Reliability
        ↓
Admin Visibility
        ↓
OD Automation
        ↓
UI Polish
```

Do not add non-essential features during the sprint without lead
approval.

------------------------------------------------------------------------

## Definition of Done

-   [ ] Only `@rajalakshmi.edu.in` users can create student sessions.
-   [ ] One event registration per student is database-enforced.
-   [ ] Registration produces an entry QR and email.
-   [ ] Entry QR is opaque, time-bound and one-time-use.
-   [ ] Multiple scanners operate concurrently without duplicate
    acceptance.
-   [ ] Physical ID-card verification is performed.
-   [ ] Present/Absent/Forgery decisions are auditable.
-   [ ] Exit QR is locked until the configured window.
-   [ ] Super Admin can bulk dispatch exit access.
-   [ ] On-spot registration cannot create duplicates.
-   [ ] OD PDF contains the required watermark.
-   [ ] OD PDF is protected from public access.
-   [ ] Admin filters/dashboard work across mobile/tablet/desktop.
-   [ ] XSS, SQLi, OAuth bypass, privilege escalation and QR race/replay
    tests pass.
-   [ ] Rate limiting and file-upload abuse tests pass.
-   [ ] Docker deployment is verified.
-   [ ] HTTPS is verified.
-   [ ] PostgreSQL backup and restore are verified.
-   [ ] Rollback/recovery path is verified.
-   [ ] Full event rehearsal is completed.

------------------------------------------------------------------------

## Key Risks

  -------------------------------------------------------------------------
  Risk                    Impact                    Mitigation
  ----------------------- ------------------------- -----------------------
  Crowd throughput        Gate queues               Multiple stations +
                                                    rehearsal

  Network reliability     Slow/rejected scans       Reliable Wi-Fi +
                                                    fallback + spare
                                                    devices

  Proxy attendance        Impersonation             Short-lived one-time
                                                    QR + physical ID

  Email delay             Missing ticket            Immediate browser
                                                    ticket + async email

  Database race           Duplicate                 Constraints + atomic
                          attendance/registration   transactions

  OD signature confusion  Compliance                Explicit
                          misunderstanding          watermarked-PDF scope

  10-day schedule         Delivery risk             Frozen MVP + parallel
                                                    work

  Device failure          Gate slowdown             Spare devices + power

  QR replay               Duplicate admission       Short validity + atomic
                                                    consumption

  Admin compromise        High privilege impact     Least privilege +
                                                    audit + recovery
  -------------------------------------------------------------------------

QR alone cannot mathematically prevent impersonation. The control is:

``` text
Opaque QR
   +
Short validity
   +
One-time consumption
   +
Physical ID-card verification
   +
Manual exception lane
```

------------------------------------------------------------------------

## Future Reusability

The application must be modular, scalable and reusable.

The immediate target is DEVS Investiture, but implementation should
support future reuse for:

-   DEVS REC website
-   Other DEVS events
-   College events
-   Multiple event configurations
-   Additional attendance workflows
-   Future document workflows

Do not prematurely create microservices.

Use:

``` text
Modular monolith
      ↓
Proven boundaries
      ↓
Measure actual requirements
      ↓
Extract services only when justified
```

Any backend module or the entire application should be capable of
evolving into a service for the future DEVS REC platform.

------------------------------------------------------------------------

## Work Assigned

  ------------------------------------------------------------------------
  Workstream        Assigned To       Primary            Status
                                      Responsibilities   
  ----------------- ----------------- ------------------ -----------------
  Frontend          Sabhari Sainath   Event Registration 
                                      module             

  Frontend          Asvand            Attendance module  
                                      and Admin          
                                      dashboard          

  Backend           Sai Kishore,      Auth, RBAC,        
                    Kamlesh           registration       
                                      endpoints, ticket  
                                      generation, QR     
                                      logic, OD PDF      

  Backend           Sarvin, Kamlesh   Role-based         
                                      routing,           
                                      attendance         
                                      scanning,          
                                      visualizations,    
                                      metrics, admin     
                                      actions            

  DevOps / Security Chandhru, Iniyan  Docker, VPS,       
                                      reverse proxy,     
                                      TLS, firewall,     
                                      DNS, secrets,      
                                      backups            

  QA / Testing      Iniyan, Chandhru  Security,          
                                      concurrency,       
                                      device/network     
                                      rehearsal,         
                                      regression         
------------------------------------------------------------------------

---

## References & Resources

The following resources are recommended references for implementation, security, architecture, and tooling used in this project.

### Authentication

- [Google Identity — OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
  - Official Google OAuth documentation.
- [Google OpenID Connect](https://developers.google.com/identity/openid-connect/openid-connect)
  - Reference for verifying Google identity and user claims.

### Frontend

- [React Documentation](https://react.dev/)
  - Official React documentation.
- [Vite Documentation](https://vite.dev/)
  - Frontend build tooling.
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
  - TypeScript language and compiler reference.
- [shadcn/ui](https://ui.shadcn.com/)
  - UI component primitives and accessibility patterns.
- [TanStack Query](https://tanstack.com/query/latest)
  - Server-state management and caching.
- [TanStack Query video tutorial](https://youtu.be/mPaCnwpFvZY?si=6mSYB6BYvSi0Qe5I)
  - Complete tutorial for tanstack query.
- [Zustand](https://zustand.docs.pmnd.rs/)
  - Client-state management.
- [Zustand Video](https://youtu.be/ULS7LHNScHc?si=K3avU7v8TL1d706_)
  - Complete tutorial for client side state management.
  

### Backend

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
  - Backend API framework.
- [FastAPI tutorial video](https://youtube.com/playlist?list=PLEt8Tae2spYnHy378vMlPH--87cfeh33P&si=1gzi1dPX4lkvQM8t)
  - An end - end tutorial for FastAPI.
- [Pydantic Documentation](https://docs.pydantic.dev/)
  - Data validation and schema definitions.
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
  - ORM and database access.
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
  - Database migration management.
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
  - Database reference.


------------------------------------------------------------------------

### Ownership rule

Each feature should have one accountable owner. Other contributors
review code and test acceptance criteria.

Avoid ownership by "everyone"; it becomes unclear during a 10-day
sprint.

------------------------------------------------------------------------

## Final Engineering Rule

Build for **correctness first, then speed**.

The most important parts are:

1.  Institutional authentication
2.  Single registration
3.  QR security
4.  Atomic attendance
5.  Concurrent scanner support
6.  Physical identity verification
7.  Auditability
8.  Security testing
9.  VPS recovery
10. Full event rehearsal

Every contributor is expected to maintain proper code quality,
documentation, Git history, commit messages, Pull Requests, testing and
security practices.

**Never directly push feature work to the upstream/main branch. Raise a
PR from your fork and let the leads review and merge it.**
