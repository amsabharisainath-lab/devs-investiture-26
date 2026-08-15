# DEVS Investiture — Frontend

React + TypeScript + Vite frontend for the **DEVS Investiture Event Registration & Attendance Platform**.

> **Location:** `client/`  
> **Design:** Black & white, Vercel-inspired, fast and information-dense

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Requirements](#requirements)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Folder Responsibilities](#folder-responsibilities)
- [Styling Rules](#styling-rules)
- [Constants](#constants)
- [State Management](#state-management)
- [API & Server State](#api--server-state)
- [Authentication](#authentication)
- [Student UI](#student-ui)
- [Checker & Admin UI](#checker--admin-ui)
- [Design System](#design-system)
- [Environment Variables](#environment-variables)
- [Development Commands](#development-commands)
- [Code Quality](#code-quality)
- [Git & Pull Requests](#git--pull-requests)
- [Adding shadcn/ui Components](#adding-shadcnui-components)
- [Frontend Definition of Done](#frontend-definition-of-done)

---

## Overview

The frontend has two primary experiences.

### Student

```text
Google Login → Registration → Entry Ticket → Exit Ticket when enabled
```

### Checker / Admin

```text
Google Login → Scanner → QR Result → ID Verification → Attendance Decision → Dashboard
```

The frontend is **not a security boundary**. Authentication, authorization, registration uniqueness, QR validity and attendance state are enforced by the FastAPI backend.

---

## Tech Stack

| Technology | Purpose |
|---|---|
| React | UI framework |
| TypeScript | Static typing |
| Vite | Development server and build tool |
| Tailwind CSS | Utility styling and design tokens |
| shadcn/ui | Shared UI primitives |
| TanStack Query | Server-state fetching, caching and invalidation |
| Zustand | Client-side state management |
| React Router | Client-side routing |
| Lucide React | Icons |
| QR scanning library | Camera-based QR scanning |
| ESLint | Static analysis |
| Prettier | Formatting |

Vite officially supports the `react-ts` template. Current Vite documentation lists Node.js `20.19+` or `22.12+` as supported baselines. citeturn0search8

---

## Requirements

Install:

- Node.js
- npm **or** pnpm
- Git

Check versions:

```bash
node --version
npm --version
pnpm --version
```

Use **one package manager per working copy**. Do not mix npm and pnpm lockfiles.

---

## Getting Started

### Using npm

If the project already exists:

```bash
cd client
npm install
npm run dev
```

### Using pnpm

```bash
cd client
pnpm install
pnpm dev
```

The development server normally runs at:

```text
http://localhost:5173
```

### Create the Vite project from scratch

#### npm

```bash
npm create vite@latest client -- --template react-ts
cd client
npm install
```

#### pnpm

```bash
pnpm create vite@latest client --template react-ts
cd client
pnpm install
```

Vite documents `react-ts` as the React + TypeScript template and supports both npm and pnpm scaffolding. citeturn0search8

---

# Project Structure

The frontend follows a **feature-oriented architecture**.

```text
client/
├── public/
│   └── ...
│
├── src/
│   ├── assets/
│   │   └── ...
│   │
│   ├── components/
│   │   ├── ui/
│   │   │   └── ...                 # shadcn/ui primitives
│   │   └── shared/
│   │       └── ...                 # reusable app components
│   │
│   ├── features/
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── api.ts
│   │   │   └── types.ts
│   │   ├── registration/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── api.ts
│   │   │   └── types.ts
│   │   ├── ticket/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── api.ts
│   │   │   └── types.ts
│   │   ├── attendance/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── api.ts
│   │   │   └── types.ts
│   │   ├── admin/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── api.ts
│   │   │   └── types.ts
│   │   └── od/
│   │       ├── components/
│   │       ├── hooks/
│   │       ├── api.ts
│   │       └── types.ts
│   │
│   ├── hooks/
│   │   └── ...                       # genuinely shared hooks
│   │
│   ├── lib/
│   │   ├── constants.ts              # application-wide constants
│   │   ├── api-client.ts             # HTTP/API client
│   │   ├── query-client.ts           # TanStack Query configuration
│   │   └── utils.ts                  # generic utilities
│   │
│   ├── pages/
│   │   └── ...                       # route-level pages
│   │
│   ├── routes/
│   │   └── ...                       # route definitions
│   │
│   ├── stores/
│   │   └── ...                       # Zustand stores
│   │
│   ├── styles/
│   │   ├── globals.css               # global CSS
│   │   ├── theme.css                 # design tokens/theme
│   │   └── ...
│   │
│   ├── types/
│   │   └── ...                       # genuinely shared types
│   │
│   ├── App.tsx
│   └── main.tsx
│
├── .env.example
├── components.json
├── eslint.config.js
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.node.json
├── vite.config.ts
└── README.md
```

### Structure rules

Feature-specific code stays inside its feature.

For example, attendance-specific:

```text
src/features/attendance/
```

owns its components, hooks, API functions and feature types.

Only genuinely reusable code belongs in shared folders.

Do not turn `src/components/` into a large collection of unrelated business components.

---

# Folder Responsibilities

## `src/components/ui/`

shadcn/ui generated primitives.

Examples:

```text
button.tsx
card.tsx
dialog.tsx
input.tsx
table.tsx
badge.tsx
```

No business logic belongs here.

## `src/components/shared/`

Reusable application components that are not tied to one feature.

Examples:

```text
PageHeader
LoadingState
EmptyState
ErrorState
ConfirmDialog
```

## `src/features/`

Business features:

```text
auth
registration
ticket
attendance
admin
od
```

Feature-specific API, hooks, types and components remain together.

## `src/pages/`

Route-level composition.

Pages should compose features instead of containing large business-logic implementations.

## `src/lib/`

Application-wide utilities and configuration.

Required files include:

```text
src/lib/constants.ts
src/lib/api-client.ts
src/lib/query-client.ts
src/lib/utils.ts
```

## `src/stores/`

Zustand stores only.

Do not duplicate server state here.

## `src/types/`

Only genuinely shared TypeScript types.

Feature-specific types should remain inside the relevant feature.

## `src/styles/`

**All custom CSS belongs here.**

Recommended:

```text
src/styles/
├── globals.css
├── theme.css
└── ...
```

Do not scatter custom CSS beside components unless a specific exception is approved.

---

# Styling Rules

The application uses a strict black-and-white visual system.

### Direction

- High contrast
- Minimal
- Technical
- Information dense
- Vercel-inspired
- No rainbow palette

### Tokens

| Token | Value |
|---|---|
| Background | `#FFFFFF`, `#FAFAFA` |
| Foreground | `#000000`, `#111111` |
| Muted | `#666666`, `#A1A1AA` |
| Border | `#E5E5E5` |
| Primary | Black |
| Destructive | Black + icon/text |
| Radius | Small/moderate |
| Typography | Inter/Geist-like sans |

Prefer Tailwind utilities and shadcn/ui components for component styling.

Custom CSS must be inside:

```text
src/styles/
```

---

# Constants

All shared application constants must be placed in:

```text
src/lib/constants.ts
```

Example:

```ts
export const APP_NAME = "DEVS Investiture";

export const INSTITUTIONAL_DOMAIN = "@rajalakshmi.edu.in";

export const USER_ROLES = {
  STUDENT: "student",
  CHECKER: "checker",
  ADMIN: "admin",
  SUPER_ADMIN: "super_admin",
} as const;

export const ATTENDANCE_STATUS = {
  PRESENT: "present",
  ABSENT: "absent",
  FORGERY: "forgery",
} as const;
```

Avoid scattering shared magic strings and numbers throughout components.

Feature-specific constants that have no shared meaning may remain inside the feature.

---

# State Management

There are two categories of state.

## Server state — TanStack Query

Use TanStack Query for:

- Current user
- Registration
- Registered students
- Attendance
- Dashboard data
- Ticket data
- OD status
- Server-backed filters/results

Install:

### npm

```bash
npm install @tanstack/react-query
```

### pnpm

```bash
pnpm add @tanstack/react-query
```

These are the current official installation commands. citeturn0search1

## Client state — Zustand

Use Zustand for genuine client state such as:

- Scanner UI state
- Temporary workflow state
- Modal state
- Local UI preferences
- Device/station UI state

Do not copy server state into Zustand.

---

# API & Server State

All HTTP communication should go through:

```text
src/lib/api-client.ts
```

Feature-specific API functions belong inside their feature:

```text
src/features/registration/api.ts
src/features/attendance/api.ts
src/features/admin/api.ts
```

Use TanStack Query around these API functions.

After mutations, invalidate only affected queries.

```text
Attendance mutation
        ↓
Invalidate affected attendance query
        ↓
Refresh relevant dashboard/list data
```

Do not invalidate the entire query cache after every mutation.

---

# Authentication

Authentication is Google OAuth/OIDC only.

The frontend:

1. Starts the Google login flow.
2. Retrieves the authenticated application session from the backend.
3. Displays UI according to the server-provided user/role.
4. Redirects users to the appropriate experience.

The frontend does **not**:

- Assign roles.
- Decide authorization.
- Decide whether a user can register.
- Trust a client-provided role.
- Store long-lived OAuth tokens in `localStorage`.
- Decide whether a QR is valid.

The FastAPI backend is authoritative.

---

# Student UI

Keep the student experience extremely short:

```text
Google Login
     ↓
Registration
     ↓
Entry Ticket
```

The ticket should display:

- Student name
- Roll number
- Event information
- Entry QR
- Ticket status
- Instructions

The QR itself must not contain sensitive student PII.

### Exit

Before the configured exit window:

```text
Exit QR
────────
LOCKED
```

When the backend enables it:

```text
Exit QR
────────
AVAILABLE
```

The frontend must use backend state rather than independently deciding when the exit window is open.

---

# Checker & Admin UI

The scanner interface is optimized for phones/tablets.

## Scanner flow

```text
Open Scanner
     ↓
Scan QR
     ↓
Show Result
     ↓
Show Student Details
     ↓
Physical ID Verification
     ↓
Present / Absent / Forgery
     ↓
Next Scan
```

The scanner should minimize taps and unnecessary navigation.

## Student verification card

Show:

- Name
- Roll number
- Department
- Year
- Registration status
- Previous attendance state
- ID verification prompt

## Admin dashboard

Show:

- Registered
- Present
- Absent/unverified
- Forgery
- Entered
- Exited
- Unresolved exceptions

Filters:

- Year
- Department
- Registration status
- Entry status
- Exit status
- Verification outcome
- Forgery
- Name
- Roll number

---

# Design System

Use shadcn/ui as the shared UI primitive layer.

Preferred components:

```text
Button
Input
Label
Card
Dialog
AlertDialog
Badge
Tabs
DropdownMenu
Table
Pagination
Select
Sheet
Skeleton
Toast
```

Scanner-specific components should be composed from these primitives:

```text
QRScanner
ScanResultCard
IdentityCheckPanel
AttendanceStatusBadge
StationHeader
```

shadcn/ui adds component source directly to the project, allowing the team to own and customize those components. citeturn0search10

---

# Environment Variables

Create local environment configuration from the example:

```bash
cp .env.example .env.local
```

Example:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Never commit `.env.local`.

Anything exposed through a `VITE_*` variable is available to the browser.

Never put secrets in frontend environment variables, including:

- Database credentials
- SMTP passwords
- Google client secrets
- Private API keys
- Server credentials

---

# Development Commands

## npm

```bash
npm install
npm run dev
npm run build
npm run preview
npm run lint
```

## pnpm

```bash
pnpm install
pnpm dev
pnpm build
pnpm preview
pnpm lint
```

The `package.json` scripts are the final source of truth if the project changes its command names.

---

# Adding shadcn/ui Components

For an existing Vite project:

### npm

```bash
npx shadcn@latest init
```

### pnpm

```bash
pnpm dlx shadcn@latest init
```

The official shadcn Vite documentation supports this initialization flow. citeturn0search0turn0search9

Add components individually:

### npm

```bash
npx shadcn@latest add button
```

### pnpm

```bash
pnpm dlx shadcn@latest add button
```

Multiple components:

```bash
pnpm dlx shadcn@latest add button card dialog input label table badge select
```

Keep generated primitives inside:

```text
src/components/ui/
```

---

# Code Quality

Before opening a PR:

```bash
npm run lint
npm run build
```

or:

```bash
pnpm lint
pnpm build
```

### Rules

- Use strict TypeScript.
- Avoid `any`.
- Prefer `unknown` with proper narrowing when input is genuinely unknown.
- Keep components small.
- Keep business logic inside features.
- Keep shared constants in `lib/constants.ts`.
- Keep custom CSS inside `styles/`.
- Use TanStack Query for server state.
- Use Zustand only for client state.
- Use shadcn/ui for shared primitives.
- Avoid unnecessary `useEffect`.
- Avoid unnecessary global state.
- Avoid magic strings/numbers.
- Avoid duplicated API logic.
- Avoid dead code.
- Do not commit secrets.
- Never rely on frontend authorization.

---

# Git & Pull Requests

Follow the repository's fork-based workflow:

```text
Fork
  ↓
Feature branch
  ↓
Implement
  ↓
Test
  ↓
Commit
  ↓
Push to fork
  ↓
Pull Request
  ↓
Review
  ↓
Merge by lead
```

**Do not directly push feature work to the upstream/main branch.**

### Commit format

```text
(scope?): short description
```

Examples:

```text
feat(registration): add student registration form
feat(attendance): add mobile QR scanner
fix(ticket): handle expired entry ticket
refactor(admin): extract attendance filters
perf(admin): reduce dashboard queries
style(ui): normalize card spacing
test(attendance): add scanner result tests
docs(client): update frontend setup
build(client): update Vite configuration
chore: update eslint configuration
```

### Dependency changes

Any dependency change must be a dedicated `chore:` commit.

Example:

```text
chore: add @tanstack/react-query to package.json
```

Do not bundle it with:

```text
feat(attendance): add attendance query hooks
```

The feature implementation must be a separate follow-up commit.

---

# Frontend Definition of Done

A frontend feature is complete when:

- [ ] UI follows the black/white design system.
- [ ] Responsive behavior works on intended devices.
- [ ] Loading state exists.
- [ ] Empty state exists where applicable.
- [ ] Error state exists where applicable.
- [ ] Accessibility has been considered.
- [ ] API errors are handled.
- [ ] No security decisions rely solely on frontend state.
- [ ] Shared primitives use shadcn/ui where appropriate.
- [ ] Shared constants are in `src/lib/constants.ts`.
- [ ] Custom CSS is inside `src/styles/`.
- [ ] Server state uses TanStack Query.
- [ ] Client state uses Zustand only where appropriate.
- [ ] TypeScript passes.
- [ ] ESLint passes.
- [ ] Production build succeeds.
- [ ] No secrets are committed.
- [ ] PR contains clear implementation and testing information.

---

## Reference Documentation

- [Vite Documentation](https://vite.dev/guide/) — setup and development workflow. citeturn0search8
- [shadcn/ui — Vite Installation](https://ui.shadcn.com/docs/installation/vite) — Vite integration. citeturn0search0
- [shadcn/ui — CLI](https://ui.shadcn.com/docs/cli) — component initialization and generation. citeturn0search9
- [TanStack Query — React Installation](https://tanstack.com/query/latest/docs/framework/react/installation) — server-state setup. citeturn0search1
