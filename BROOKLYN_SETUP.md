# Brooklyn Setup

Brooklyn is a separate project from Groundwork.

Do not reuse Groundwork repositories, deployments, databases, API keys, env files, or assistant memory.

## Project IDs

- Local folder: `/Users/bunkerwimer/Desktop/Brooklyn Project`
- GitHub repo: `bunkerwimer/brooklyn`
- Vercel project: `brooklyn`
- Supabase project: `brooklyn`

## Environment Variables

Keep these in Brooklyn only.

```env
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=
```

If Brooklyn later needs server-side database writes, add this only to server environments:

```env
SUPABASE_SERVICE_ROLE_KEY=
```

Never use `NEXT_PUBLIC_` for service-role keys.

## Separation Checklist

- Brooklyn code lives only in `/Users/bunkerwimer/Desktop/Brooklyn Project`.
- Groundwork code lives only in `/Users/bunkerwimer/Downloads/Bunker's Presentation software`.
- Brooklyn Vercel env vars must point only to the Brooklyn Supabase project.
- Groundwork Vercel env vars must point only to the Groundwork Supabase project.
- Keep `.claude/`, `.vercel/`, `.supabase/`, and `.env*` out of git.
