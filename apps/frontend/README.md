# Pulse AI Studio - Frontend

Next.js 15 (App Router) frontend with TypeScript, Tailwind CSS, and shadcn/ui.

## Features

- **Next.js 15 App Router** with route groups
- **Arabic/English i18n** with RTL support
- **Tailwind CSS** + **shadcn/ui** components
- **React Query** for data fetching
- **TypeScript** for type safety
- **Responsive design** (mobile-first)

## Setup

```bash
cd apps/frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local
# Edit .env.local with API URLs

# Run development server
npm run dev
```

Visit `http://localhost:3000`

## Project Structure

```
apps/frontend/
├── app/
│   ├── (landing)/             # Landing page (public)
│   │   └── page.tsx
│   ├── (app)/                 # Authenticated app (route group)
│   │   ├── chat/
│   │   ├── cv/
│   │   ├── slides/
│   │   ├── image/
│   │   ├── video/
│   │   └── account/
│   ├── layout.tsx             # Root layout
│   └── providers.tsx          # React Query provider
├── components/                 # Reusable components
│   ├── ModelSelector.tsx
│   ├── TokenMeter.tsx
│   ├── PlanCard.tsx
│   ├── PayButton.tsx
│   └── ...
├── lib/                        # Utilities
│   ├── api.ts                 # API client
│   └── utils.ts
├── styles/
│   └── globals.css
├── public/
├── package.json
├── tsconfig.json
├── next.config.js
├── tailwind.config.ts
└── postcss.config.js
```

## Routes

### Public Routes
- `/` - Landing page

### Authenticated Routes
- `/app/chat` - AI Chat
- `/app/cv` - CV Maker
- `/app/slides` - Slide Maker
- `/app/image` - Image Generator & Editor
- `/app/video` - Video Generator & Editor
- `/app/account` - Account & Billing

## i18n (Arabic/English)

Default language is Arabic (RTL). Toggle to English via UI component.

## Components (shadcn/ui)

Install components as needed:
```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add toast
```

## Deployment

Built as Docker image and deployed to AWS ECS Fargate. See `/docker/frontend.Dockerfile`.

## Scripts

- `npm run dev` - Development server
- `npm run build` - Production build
- `npm run start` - Start production server
- `npm run lint` - ESLint
- `npm run type-check` - TypeScript check
