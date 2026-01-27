# Веб-разработка 2026

## Frontend Frameworks

### React 19+
```tsx
// Server Components (по умолчанию)
async function UserList() {
  const users = await db.users.findMany();
  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}

// Client Components
'use client';
import { useState, useTransition } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  const [isPending, startTransition] = useTransition();
  
  const handleClick = () => {
    startTransition(() => {
      setCount(c => c + 1);
    });
  };
  
  return (
    <button onClick={handleClick} disabled={isPending}>
      Count: {count}
    </button>
  );
}

// Actions (Server Actions)
async function createUser(formData: FormData) {
  'use server';
  const name = formData.get('name');
  await db.users.create({ data: { name } });
  revalidatePath('/users');
}

function CreateUserForm() {
  return (
    <form action={createUser}>
      <input name="name" required />
      <button type="submit">Create</button>
    </form>
  );
}

// Hooks
import { use, useMemo, useCallback, useRef, useEffect } from 'react';

function DataComponent({ dataPromise }) {
  const data = use(dataPromise); // Suspense для промисов
  
  const memoizedValue = useMemo(() => 
    expensiveCalculation(data), [data]
  );
  
  const handleClick = useCallback(() => {
    console.log(data);
  }, [data]);
  
  const ref = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    // Side effects
    return () => { /* cleanup */ };
  }, []);
  
  return <div ref={ref}>{memoizedValue}</div>;
}

// Context
const ThemeContext = createContext<'light' | 'dark'>('light');

function App() {
  return (
    <ThemeContext.Provider value="dark">
      <Main />
    </ThemeContext.Provider>
  );
}

function ThemedButton() {
  const theme = useContext(ThemeContext);
  return <button className={theme}>Click</button>;
}
```

### Next.js 15+
```tsx
// app/layout.tsx
export default function RootLayout({ children }) {
  return (
    <html>
      <body>{children}</body>
    </html>
  );
}

// app/page.tsx
export default async function Home() {
  const data = await fetch('https://api.example.com/data', {
    next: { revalidate: 3600 } // ISR
  });
  
  return <main>{/* content */}</main>;
}

// app/users/[id]/page.tsx
export async function generateStaticParams() {
  const users = await getUsers();
  return users.map(user => ({ id: user.id.toString() }));
}

export default async function UserPage({ params }) {
  const user = await getUser(params.id);
  return <div>{user.name}</div>;
}

// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const users = await db.users.findMany();
  return NextResponse.json(users);
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  const user = await db.users.create({ data: body });
  return NextResponse.json(user, { status: 201 });
}

// Middleware
export function middleware(request: NextRequest) {
  const token = request.cookies.get('token');
  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
}

export const config = {
  matcher: ['/dashboard/:path*', '/api/:path*'],
};
```

### Vue 3.4+
```vue
<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';

interface User {
  id: number;
  name: string;
}

const props = defineProps<{
  initialCount?: number;
}>();

const emit = defineEmits<{
  (e: 'update', value: number): void;
}>();

const count = ref(props.initialCount ?? 0);
const users = ref<User[]>([]);

const doubleCount = computed(() => count.value * 2);

watch(count, (newVal, oldVal) => {
  console.log(`Count changed from ${oldVal} to ${newVal}`);
});

onMounted(async () => {
  users.value = await fetchUsers();
});

function increment() {
  count.value++;
  emit('update', count.value);
}
</script>

<template>
  <div>
    <button @click="increment">Count: {{ count }}</button>
    <p>Double: {{ doubleCount }}</p>
    
    <ul>
      <li v-for="user in users" :key="user.id">
        {{ user.name }}
      </li>
    </ul>
  </div>
</template>

<style scoped>
button {
  padding: 0.5rem 1rem;
}
</style>
```

### Nuxt 3.10+
```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  modules: ['@nuxtjs/tailwindcss', '@pinia/nuxt'],
  runtimeConfig: {
    apiSecret: process.env.API_SECRET,
    public: {
      apiBase: process.env.API_BASE,
    },
  },
});

// composables/useApi.ts
export const useApi = () => {
  const config = useRuntimeConfig();
  
  const fetch = async <T>(endpoint: string): Promise<T> => {
    return await $fetch(`${config.public.apiBase}${endpoint}`);
  };
  
  return { fetch };
};

// pages/users/[id].vue
<script setup lang="ts">
const route = useRoute();
const { data: user } = await useFetch(`/api/users/${route.params.id}`);
</script>

// server/api/users/[id].ts
export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id');
  return await db.users.findUnique({ where: { id: Number(id) } });
});
```

### Svelte 5+
```svelte
<script lang="ts">
  // Runes (Svelte 5)
  let count = $state(0);
  let doubled = $derived(count * 2);
  
  interface User {
    id: number;
    name: string;
  }
  
  let { users = [] }: { users: User[] } = $props();
  
  $effect(() => {
    console.log(`Count is now ${count}`);
    return () => {
      console.log('Cleanup');
    };
  });
  
  function increment() {
    count++;
  }
</script>

<button onclick={increment}>
  Count: {count} (doubled: {doubled})
</button>

<ul>
  {#each users as user (user.id)}
    <li>{user.name}</li>
  {/each}
</ul>

{#if count > 10}
  <p>Count is high!</p>
{:else}
  <p>Count is low</p>
{/if}

<style>
  button {
    padding: 0.5rem 1rem;
  }
</style>
```

---

## CSS Frameworks

### Tailwind CSS 4.0
```html
<!-- Utility-first -->
<div class="flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-md">
  <h2 class="text-xl font-bold text-gray-900 dark:text-white">Title</h2>
  <button class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-md transition-colors">
    Click
  </button>
</div>

<!-- Responsive -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <div class="p-4 bg-white rounded-lg">Card 1</div>
  <div class="p-4 bg-white rounded-lg">Card 2</div>
  <div class="p-4 bg-white rounded-lg">Card 3</div>
</div>

<!-- Animations -->
<div class="animate-pulse bg-gray-200 h-4 rounded"></div>
<div class="hover:scale-105 transition-transform duration-300"></div>

<!-- Custom variants -->
<div class="group">
  <span class="group-hover:text-blue-500">Hover parent</span>
</div>
```

```javascript
// tailwind.config.js (v4)
export default {
  content: ['./src/**/*.{html,js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          500: '#0ea5e9',
          900: '#0c4a6e',
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};
```

---

## Backend Frameworks

### Node.js + Express/Fastify
```typescript
// Express
import express from 'express';
import { z } from 'zod';

const app = express();
app.use(express.json());

const UserSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
});

app.post('/users', async (req, res) => {
  try {
    const data = UserSchema.parse(req.body);
    const user = await db.users.create({ data });
    res.status(201).json(user);
  } catch (error) {
    res.status(400).json({ error: 'Invalid data' });
  }
});

// Fastify
import Fastify from 'fastify';

const fastify = Fastify({ logger: true });

fastify.post('/users', {
  schema: {
    body: {
      type: 'object',
      required: ['name', 'email'],
      properties: {
        name: { type: 'string' },
        email: { type: 'string', format: 'email' },
      },
    },
  },
}, async (request, reply) => {
  const user = await db.users.create({ data: request.body });
  return user;
});

await fastify.listen({ port: 3000 });
```

### Django 5.0+
```python
# models.py
from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

# views.py
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class UserView(View):
    async def get(self, request):
        users = [u async for u in User.objects.all()]
        return JsonResponse({'users': [{'id': u.id, 'name': u.name} for u in users]})
    
    async def post(self, request):
        import json
        data = json.loads(request.body)
        user = await User.objects.acreate(**data)
        return JsonResponse({'id': user.id, 'name': user.name}, status=201)

# Django REST Framework
from rest_framework import viewsets, serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'created_at']

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
```

### Laravel 11+
```php
<?php

// Model
namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class User extends Model
{
    protected $fillable = ['name', 'email'];
    
    protected $casts = [
        'email_verified_at' => 'datetime',
    ];
    
    public function posts(): HasMany
    {
        return $this->hasMany(Post::class);
    }
}

// Controller
namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\Request;

class UserController extends Controller
{
    public function index()
    {
        return User::with('posts')->paginate(15);
    }
    
    public function store(Request $request)
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'email' => 'required|email|unique:users',
        ]);
        
        return User::create($validated);
    }
}

// Routes (api.php)
use App\Http\Controllers\UserController;

Route::apiResource('users', UserController::class);
```

---

## Databases & ORMs

### Prisma (Node.js)
```prisma
// schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String?
  posts     Post[]
  profile   Profile?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

model Post {
  id        Int      @id @default(autoincrement())
  title     String
  content   String?
  published Boolean  @default(false)
  author    User     @relation(fields: [authorId], references: [id])
  authorId  Int
}
```

```typescript
// Usage
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// Create
const user = await prisma.user.create({
  data: {
    email: 'john@example.com',
    name: 'John',
    posts: {
      create: [
        { title: 'First Post', content: 'Hello!' },
      ],
    },
  },
  include: { posts: true },
});

// Query
const users = await prisma.user.findMany({
  where: {
    email: { contains: '@example.com' },
  },
  include: {
    posts: {
      where: { published: true },
    },
  },
  orderBy: { createdAt: 'desc' },
  take: 10,
});

// Transaction
const [user, post] = await prisma.$transaction([
  prisma.user.create({ data: { email: 'new@example.com' } }),
  prisma.post.create({ data: { title: 'New', authorId: 1 } }),
]);
```

### Drizzle ORM
```typescript
import { pgTable, serial, text, timestamp, boolean } from 'drizzle-orm/pg-core';
import { drizzle } from 'drizzle-orm/node-postgres';
import { eq, and, or, like } from 'drizzle-orm';

// Schema
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  email: text('email').notNull().unique(),
  createdAt: timestamp('created_at').defaultNow(),
});

export const posts = pgTable('posts', {
  id: serial('id').primaryKey(),
  title: text('title').notNull(),
  content: text('content'),
  published: boolean('published').default(false),
  authorId: integer('author_id').references(() => users.id),
});

// Queries
const db = drizzle(pool);

const allUsers = await db.select().from(users);

const userWithPosts = await db
  .select()
  .from(users)
  .leftJoin(posts, eq(users.id, posts.authorId))
  .where(eq(users.id, 1));

await db.insert(users).values({ name: 'John', email: 'john@example.com' });

await db.update(users).set({ name: 'Jane' }).where(eq(users.id, 1));

await db.delete(users).where(eq(users.id, 1));
```

---

## API Design

### REST API
```yaml
# OpenAPI 3.1
openapi: 3.1.0
info:
  title: User API
  version: 1.0.0

paths:
  /users:
    get:
      summary: List users
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 10
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  meta:
                    $ref: '#/components/schemas/Pagination'
    
    post:
      summary: Create user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUser'
      responses:
        '201':
          description: Created

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        email:
          type: string
          format: email
```

### GraphQL
```graphql
# Schema
type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]!
  createdAt: DateTime!
}

type Post {
  id: ID!
  title: String!
  content: String
  author: User!
  published: Boolean!
}

type Query {
  users(page: Int, limit: Int): [User!]!
  user(id: ID!): User
  posts(published: Boolean): [Post!]!
}

type Mutation {
  createUser(input: CreateUserInput!): User!
  updateUser(id: ID!, input: UpdateUserInput!): User!
  deleteUser(id: ID!): Boolean!
}

input CreateUserInput {
  name: String!
  email: String!
}

input UpdateUserInput {
  name: String
  email: String
}
```

```typescript
// Resolvers
const resolvers = {
  Query: {
    users: async (_, { page = 1, limit = 10 }) => {
      return db.users.findMany({
        skip: (page - 1) * limit,
        take: limit,
      });
    },
    user: async (_, { id }) => {
      return db.users.findUnique({ where: { id } });
    },
  },
  Mutation: {
    createUser: async (_, { input }) => {
      return db.users.create({ data: input });
    },
  },
  User: {
    posts: async (parent) => {
      return db.posts.findMany({ where: { authorId: parent.id } });
    },
  },
};
```

---

## Authentication

### JWT + OAuth 2.0
```typescript
import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';

// JWT
const generateTokens = (user: User) => {
  const accessToken = jwt.sign(
    { userId: user.id, email: user.email },
    process.env.JWT_SECRET!,
    { expiresIn: '15m' }
  );
  
  const refreshToken = jwt.sign(
    { userId: user.id },
    process.env.JWT_REFRESH_SECRET!,
    { expiresIn: '7d' }
  );
  
  return { accessToken, refreshToken };
};

const verifyToken = (token: string) => {
  return jwt.verify(token, process.env.JWT_SECRET!);
};

// Password hashing
const hashPassword = async (password: string) => {
  return bcrypt.hash(password, 12);
};

const verifyPassword = async (password: string, hash: string) => {
  return bcrypt.compare(password, hash);
};

// OAuth 2.0 (Google)
import { OAuth2Client } from 'google-auth-library';

const client = new OAuth2Client(process.env.GOOGLE_CLIENT_ID);

const verifyGoogleToken = async (token: string) => {
  const ticket = await client.verifyIdToken({
    idToken: token,
    audience: process.env.GOOGLE_CLIENT_ID,
  });
  return ticket.getPayload();
};
```

---

## Testing

### Jest + Testing Library
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { rest } from 'msw';
import { setupServer } from 'msw/node';

// Component test
describe('Counter', () => {
  it('increments count on click', async () => {
    render(<Counter />);
    
    const button = screen.getByRole('button', { name: /count/i });
    expect(button).toHaveTextContent('Count: 0');
    
    await userEvent.click(button);
    expect(button).toHaveTextContent('Count: 1');
  });
});

// API mock
const server = setupServer(
  rest.get('/api/users', (req, res, ctx) => {
    return res(ctx.json([{ id: 1, name: 'John' }]));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// Integration test
describe('UserList', () => {
  it('loads and displays users', async () => {
    render(<UserList />);
    
    await waitFor(() => {
      expect(screen.getByText('John')).toBeInTheDocument();
    });
  });
});
```

### Playwright (E2E)
```typescript
import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('user can login', async ({ page }) => {
    await page.goto('/login');
    
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('h1')).toContainText('Welcome');
  });
  
  test('shows error for invalid credentials', async ({ page }) => {
    await page.goto('/login');
    
    await page.fill('[name="email"]', 'wrong@example.com');
    await page.fill('[name="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.error')).toBeVisible();
  });
});
```

---

## DevOps & Deployment

### Docker
```dockerfile
# Multi-stage build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/app
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=postgres
  
  redis:
    image: redis:7-alpine

volumes:
  postgres_data:
```

### CI/CD (GitHub Actions)
```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm test
      - run: npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to production
        run: |
          # Deploy commands
```

Источники: MDN, официальная документация фреймворков, 2024-2026
