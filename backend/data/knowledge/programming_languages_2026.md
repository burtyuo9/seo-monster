# Языки программирования 2026

## Python 3.12+

### Основы
```python
# Типизация (обязательна в 2026)
from typing import List, Dict, Optional, Union, TypeVar, Generic

def process_data(items: List[str], config: Optional[Dict[str, any]] = None) -> Dict[str, int]:
    result: Dict[str, int] = {}
    for item in items:
        result[item] = len(item)
    return result

# Pattern matching (match/case)
def handle_response(response: dict) -> str:
    match response:
        case {"status": 200, "data": data}:
            return f"Success: {data}"
        case {"status": 404}:
            return "Not found"
        case {"status": status} if status >= 500:
            return f"Server error: {status}"
        case _:
            return "Unknown response"

# Dataclasses
from dataclasses import dataclass, field

@dataclass
class User:
    id: int
    name: str
    email: str
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.email = self.email.lower()

# Async/await
import asyncio
import aiohttp

async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def main():
    urls = ["https://api1.com", "https://api2.com"]
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

# Context managers
from contextlib import asynccontextmanager

@asynccontextmanager
async def managed_resource():
    resource = await acquire_resource()
    try:
        yield resource
    finally:
        await release_resource(resource)
```

### Популярные библиотеки 2026

```python
# FastAPI - веб-фреймворк
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.post("/items/")
async def create_item(item: Item):
    return {"item": item, "status": "created"}

# SQLAlchemy 2.0 - ORM
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

# Pandas - анализ данных
import pandas as pd

df = pd.read_csv("data.csv")
df_filtered = df[df["value"] > 100].groupby("category").agg({
    "value": ["mean", "sum", "count"]
})

# NumPy - вычисления
import numpy as np

arr = np.array([[1, 2, 3], [4, 5, 6]])
result = np.dot(arr, arr.T)

# PyTorch - машинное обучение
import torch
import torch.nn as nn

class SimpleNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 128)
        self.fc2 = nn.Linear(128, 10)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        return self.fc2(x)
```

---

## JavaScript/TypeScript (ES2026)

### TypeScript 5.x
```typescript
// Строгая типизация
interface User {
  id: number;
  name: string;
  email: string;
  roles: Role[];
  metadata?: Record<string, unknown>;
}

type Role = 'admin' | 'user' | 'moderator';

// Generics
function fetchData<T>(url: string): Promise<T> {
  return fetch(url).then(res => res.json());
}

// Utility types
type PartialUser = Partial<User>;
type RequiredUser = Required<User>;
type ReadonlyUser = Readonly<User>;
type UserWithoutRoles = Omit<User, 'roles'>;
type UserIdAndName = Pick<User, 'id' | 'name'>;

// Conditional types
type NonNullable<T> = T extends null | undefined ? never : T;

// Template literal types
type EventName = `on${Capitalize<string>}`;
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';
type Endpoint = `/${string}`;

// Decorators (стабильные в 2026)
function log(target: any, key: string, descriptor: PropertyDescriptor) {
  const original = descriptor.value;
  descriptor.value = function(...args: any[]) {
    console.log(`Calling ${key} with`, args);
    return original.apply(this, args);
  };
  return descriptor;
}

class Service {
  @log
  async fetchUser(id: number): Promise<User> {
    // ...
  }
}

// Satisfies operator
const config = {
  apiUrl: 'https://api.example.com',
  timeout: 5000,
} satisfies Record<string, string | number>;
```

### Modern JavaScript
```javascript
// Top-level await
const data = await fetch('/api/data').then(r => r.json());

// Private class fields
class Counter {
  #count = 0;
  
  increment() {
    this.#count++;
  }
  
  get value() {
    return this.#count;
  }
}

// Optional chaining & nullish coalescing
const userName = user?.profile?.name ?? 'Anonymous';

// Array methods
const items = [1, 2, 3, 4, 5];
const doubled = items.map(x => x * 2);
const filtered = items.filter(x => x > 2);
const sum = items.reduce((acc, x) => acc + x, 0);
const found = items.find(x => x === 3);
const hasEven = items.some(x => x % 2 === 0);
const allPositive = items.every(x => x > 0);

// Object methods
const obj = { a: 1, b: 2, c: 3 };
const entries = Object.entries(obj);
const keys = Object.keys(obj);
const values = Object.values(obj);
const fromEntries = Object.fromEntries([['a', 1], ['b', 2]]);

// Spread & destructuring
const merged = { ...obj1, ...obj2 };
const [first, ...rest] = items;
const { a, b, ...others } = obj;

// Promises & async
const results = await Promise.all([fetch(url1), fetch(url2)]);
const firstResult = await Promise.race([fetch(url1), fetch(url2)]);
const settled = await Promise.allSettled([fetch(url1), fetch(url2)]);
```

---

## Go (Golang) 1.22+

```go
package main

import (
    "context"
    "encoding/json"
    "fmt"
    "net/http"
    "sync"
    "time"
)

// Структуры и методы
type User struct {
    ID        int       `json:"id"`
    Name      string    `json:"name"`
    Email     string    `json:"email"`
    CreatedAt time.Time `json:"created_at"`
}

func (u *User) Validate() error {
    if u.Name == "" {
        return fmt.Errorf("name is required")
    }
    return nil
}

// Generics (с Go 1.18+)
func Map[T, U any](items []T, fn func(T) U) []U {
    result := make([]U, len(items))
    for i, item := range items {
        result[i] = fn(item)
    }
    return result
}

func Filter[T any](items []T, fn func(T) bool) []T {
    var result []T
    for _, item := range items {
        if fn(item) {
            result = append(result, item)
        }
    }
    return result
}

// Горутины и каналы
func fetchURLs(urls []string) []string {
    results := make(chan string, len(urls))
    var wg sync.WaitGroup
    
    for _, url := range urls {
        wg.Add(1)
        go func(u string) {
            defer wg.Done()
            resp, err := http.Get(u)
            if err != nil {
                results <- fmt.Sprintf("Error: %v", err)
                return
            }
            defer resp.Body.Close()
            results <- fmt.Sprintf("OK: %s", u)
        }(url)
    }
    
    go func() {
        wg.Wait()
        close(results)
    }()
    
    var output []string
    for r := range results {
        output = append(output, r)
    }
    return output
}

// Context для отмены
func fetchWithTimeout(ctx context.Context, url string) ([]byte, error) {
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()
    
    req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
    if err != nil {
        return nil, err
    }
    
    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    
    return io.ReadAll(resp.Body)
}

// HTTP сервер
func main() {
    http.HandleFunc("/api/users", func(w http.ResponseWriter, r *http.Request) {
        users := []User{{ID: 1, Name: "John"}}
        json.NewEncoder(w).Encode(users)
    })
    
    http.ListenAndServe(":8080", nil)
}
```

---

## Rust 2024+

```rust
use std::collections::HashMap;
use tokio;
use serde::{Deserialize, Serialize};

// Структуры и трейты
#[derive(Debug, Clone, Serialize, Deserialize)]
struct User {
    id: u64,
    name: String,
    email: String,
}

impl User {
    fn new(id: u64, name: &str, email: &str) -> Self {
        Self {
            id,
            name: name.to_string(),
            email: email.to_string(),
        }
    }
    
    fn validate(&self) -> Result<(), String> {
        if self.name.is_empty() {
            return Err("Name is required".to_string());
        }
        Ok(())
    }
}

// Generics и traits
trait Repository<T> {
    fn find(&self, id: u64) -> Option<&T>;
    fn save(&mut self, item: T) -> Result<(), String>;
}

struct InMemoryRepo<T> {
    items: HashMap<u64, T>,
}

impl<T> Repository<T> for InMemoryRepo<T> {
    fn find(&self, id: u64) -> Option<&T> {
        self.items.get(&id)
    }
    
    fn save(&mut self, item: T) -> Result<(), String> {
        // Implementation
        Ok(())
    }
}

// Error handling
fn divide(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 {
        Err("Division by zero".to_string())
    } else {
        Ok(a / b)
    }
}

// Pattern matching
fn process_option(opt: Option<i32>) -> String {
    match opt {
        Some(x) if x > 0 => format!("Positive: {}", x),
        Some(x) if x < 0 => format!("Negative: {}", x),
        Some(0) => "Zero".to_string(),
        None => "Nothing".to_string(),
        _ => "Unknown".to_string(),
    }
}

// Async/await
#[tokio::main]
async fn main() {
    let response = reqwest::get("https://api.example.com/data")
        .await
        .unwrap()
        .json::<Vec<User>>()
        .await
        .unwrap();
    
    println!("{:?}", response);
}

// Iterators
fn process_items(items: Vec<i32>) -> Vec<i32> {
    items.iter()
        .filter(|&x| *x > 0)
        .map(|x| x * 2)
        .collect()
}
```

---

## C++ (C++23)

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <ranges>
#include <format>
#include <expected>

// Современный C++
class User {
public:
    User(int id, std::string name) : id_(id), name_(std::move(name)) {}
    
    [[nodiscard]] int id() const { return id_; }
    [[nodiscard]] const std::string& name() const { return name_; }
    
private:
    int id_;
    std::string name_;
};

// Smart pointers
auto createUser(int id, const std::string& name) {
    return std::make_unique<User>(id, name);
}

// Ranges (C++20/23)
void processItems(const std::vector<int>& items) {
    auto result = items 
        | std::views::filter([](int x) { return x > 0; })
        | std::views::transform([](int x) { return x * 2; });
    
    for (int x : result) {
        std::cout << x << " ";
    }
}

// std::expected (C++23)
std::expected<int, std::string> divide(int a, int b) {
    if (b == 0) {
        return std::unexpected("Division by zero");
    }
    return a / b;
}

// std::format (C++20)
void printUser(const User& user) {
    std::cout << std::format("User: id={}, name={}\n", user.id(), user.name());
}

// Concepts (C++20)
template<typename T>
concept Numeric = std::integral<T> || std::floating_point<T>;

template<Numeric T>
T add(T a, T b) {
    return a + b;
}

// Lambda expressions
auto multiply = [](int a, int b) { return a * b; };
auto genericLambda = []<typename T>(T a, T b) { return a + b; };
```

---

## Java 21+ (LTS)

```java
// Records (immutable data classes)
public record User(int id, String name, String email) {
    public User {
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("Name is required");
        }
    }
}

// Sealed classes
public sealed interface Shape permits Circle, Rectangle, Triangle {
    double area();
}

public record Circle(double radius) implements Shape {
    public double area() { return Math.PI * radius * radius; }
}

// Pattern matching
public String describe(Object obj) {
    return switch (obj) {
        case Integer i -> "Integer: " + i;
        case String s when s.length() > 5 -> "Long string: " + s;
        case String s -> "Short string: " + s;
        case null -> "Null value";
        default -> "Unknown: " + obj;
    };
}

// Virtual threads (Project Loom)
public void processWithVirtualThreads(List<String> urls) throws Exception {
    try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
        var futures = urls.stream()
            .map(url -> executor.submit(() -> fetch(url)))
            .toList();
        
        for (var future : futures) {
            System.out.println(future.get());
        }
    }
}

// Stream API
public List<String> processUsers(List<User> users) {
    return users.stream()
        .filter(u -> u.email().contains("@"))
        .map(User::name)
        .sorted()
        .distinct()
        .toList();
}

// Optional
public String getUserName(Long id) {
    return findUserById(id)
        .map(User::name)
        .orElse("Unknown");
}
```

---

## C# 12+ (.NET 8)

```csharp
// Primary constructors
public class User(int id, string name, string email)
{
    public int Id => id;
    public string Name => name;
    public string Email => email;
}

// Records
public record UserRecord(int Id, string Name, string Email);

// Pattern matching
public string Describe(object obj) => obj switch
{
    int i when i > 0 => $"Positive: {i}",
    int i when i < 0 => $"Negative: {i}",
    string { Length: > 5 } s => $"Long string: {s}",
    string s => $"Short string: {s}",
    null => "Null",
    _ => "Unknown"
};

// LINQ
public IEnumerable<string> ProcessUsers(IEnumerable<User> users)
{
    return users
        .Where(u => u.Email.Contains("@"))
        .OrderBy(u => u.Name)
        .Select(u => u.Name)
        .Distinct();
}

// Async/await
public async Task<List<User>> FetchUsersAsync(IEnumerable<string> urls)
{
    var tasks = urls.Select(url => httpClient.GetFromJsonAsync<User>(url));
    var results = await Task.WhenAll(tasks);
    return results.Where(u => u != null).ToList()!;
}

// Collection expressions (C# 12)
int[] numbers = [1, 2, 3, 4, 5];
List<string> names = ["Alice", "Bob", "Charlie"];

// Required members
public class Config
{
    public required string ApiKey { get; init; }
    public required string BaseUrl { get; init; }
}
```

---

## PHP 8.3+

```php
<?php

// Typed properties and constructor promotion
class User
{
    public function __construct(
        public readonly int $id,
        public string $name,
        public string $email,
        public array $roles = [],
    ) {}
}

// Enums
enum Status: string
{
    case Active = 'active';
    case Inactive = 'inactive';
    case Pending = 'pending';
    
    public function label(): string
    {
        return match($this) {
            self::Active => 'Active User',
            self::Inactive => 'Inactive User',
            self::Pending => 'Pending Approval',
        };
    }
}

// Attributes
#[Route('/api/users', methods: ['GET'])]
#[Middleware('auth')]
class UserController
{
    #[Inject]
    private UserRepository $repository;
    
    public function index(): array
    {
        return $this->repository->findAll();
    }
}

// Match expression
function getStatusCode(string $status): int
{
    return match($status) {
        'success' => 200,
        'created' => 201,
        'not_found' => 404,
        'error' => 500,
        default => 400,
    };
}

// Named arguments
$user = new User(
    id: 1,
    name: 'John',
    email: 'john@example.com',
    roles: ['admin'],
);

// Null-safe operator
$userName = $user?->profile?->name ?? 'Anonymous';

// First-class callable syntax
$callback = $user->getName(...);
$filtered = array_filter($users, $validator->isValid(...));
```

---

## Ruby 3.3+

```ruby
# Typed signatures (RBS)
# sig/user.rbs
# class User
#   attr_reader id: Integer
#   attr_reader name: String
#   def initialize: (Integer id, String name) -> void
# end

class User
  attr_reader :id, :name, :email
  
  def initialize(id:, name:, email:)
    @id = id
    @name = name
    @email = email
  end
  
  def to_h
    { id: @id, name: @name, email: @email }
  end
end

# Pattern matching
def process(data)
  case data
  in { status: 'success', data: { users: [first, *rest] } }
    puts "First user: #{first}"
  in { status: 'error', message: }
    puts "Error: #{message}"
  in [Integer => x, Integer => y]
    puts "Coordinates: #{x}, #{y}"
  else
    puts "Unknown format"
  end
end

# Ractors (parallelism)
results = 4.times.map do |i|
  Ractor.new(i) do |n|
    n * 2
  end
end.map(&:take)

# Fiber scheduler (async)
require 'async'

Async do |task|
  urls = ['https://api1.com', 'https://api2.com']
  
  responses = urls.map do |url|
    task.async do
      HTTP.get(url)
    end
  end.map(&:wait)
end

# Method chaining
users
  .select { |u| u.active? }
  .map(&:name)
  .sort
  .uniq
```

---

## Swift 5.9+

```swift
import Foundation

// Structs and classes
struct User: Codable, Identifiable {
    let id: Int
    var name: String
    var email: String
    var roles: [String] = []
}

// Protocols
protocol Repository {
    associatedtype Entity
    func find(id: Int) async throws -> Entity?
    func save(_ entity: Entity) async throws
}

// Async/await
func fetchUsers() async throws -> [User] {
    let url = URL(string: "https://api.example.com/users")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode([User].self, from: data)
}

// Result builders
@resultBuilder
struct HTMLBuilder {
    static func buildBlock(_ components: String...) -> String {
        components.joined()
    }
}

@HTMLBuilder
func buildPage() -> String {
    "<html>"
    "<body>"
    "<h1>Hello</h1>"
    "</body>"
    "</html>"
}

// Property wrappers
@propertyWrapper
struct Clamped<Value: Comparable> {
    var value: Value
    let range: ClosedRange<Value>
    
    var wrappedValue: Value {
        get { value }
        set { value = min(max(newValue, range.lowerBound), range.upperBound) }
    }
}

// Actors (concurrency)
actor UserCache {
    private var cache: [Int: User] = [:]
    
    func get(_ id: Int) -> User? {
        cache[id]
    }
    
    func set(_ user: User) {
        cache[user.id] = user
    }
}
```

---

## Kotlin 2.0+

```kotlin
// Data classes
data class User(
    val id: Int,
    val name: String,
    val email: String,
    val roles: List<String> = emptyList()
)

// Sealed classes
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// Extension functions
fun String.isValidEmail(): Boolean {
    return this.contains("@") && this.contains(".")
}

// Coroutines
suspend fun fetchUsers(): List<User> {
    return withContext(Dispatchers.IO) {
        api.getUsers()
    }
}

fun main() = runBlocking {
    val users = async { fetchUsers() }
    val posts = async { fetchPosts() }
    
    println("Users: ${users.await()}")
    println("Posts: ${posts.await()}")
}

// Flow
fun observeUsers(): Flow<List<User>> = flow {
    while (true) {
        emit(fetchUsers())
        delay(5000)
    }
}

// DSL
fun html(init: HTML.() -> Unit): HTML {
    val html = HTML()
    html.init()
    return html
}

val page = html {
    head {
        title("My Page")
    }
    body {
        h1("Hello, World!")
        p("This is a paragraph")
    }
}

// Null safety
fun processUser(user: User?) {
    val name = user?.name ?: "Unknown"
    user?.let { println("User: ${it.name}") }
    user?.also { saveToDatabase(it) }
}
```

---

## SQL (PostgreSQL 16+, MySQL 8+)

```sql
-- Common Table Expressions (CTE)
WITH active_users AS (
    SELECT * FROM users WHERE status = 'active'
),
user_orders AS (
    SELECT user_id, COUNT(*) as order_count, SUM(total) as total_spent
    FROM orders
    GROUP BY user_id
)
SELECT 
    u.name,
    u.email,
    COALESCE(uo.order_count, 0) as orders,
    COALESCE(uo.total_spent, 0) as spent
FROM active_users u
LEFT JOIN user_orders uo ON u.id = uo.user_id
ORDER BY spent DESC;

-- Window functions
SELECT 
    name,
    department,
    salary,
    AVG(salary) OVER (PARTITION BY department) as dept_avg,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) as rank_in_dept,
    LAG(salary) OVER (ORDER BY hire_date) as prev_salary
FROM employees;

-- JSON operations (PostgreSQL)
SELECT 
    data->>'name' as name,
    data->'address'->>'city' as city,
    jsonb_array_elements(data->'tags') as tag
FROM documents
WHERE data @> '{"status": "active"}';

-- Recursive CTE
WITH RECURSIVE category_tree AS (
    SELECT id, name, parent_id, 1 as level
    FROM categories
    WHERE parent_id IS NULL
    
    UNION ALL
    
    SELECT c.id, c.name, c.parent_id, ct.level + 1
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT * FROM category_tree ORDER BY level, name;

-- Upsert (INSERT ON CONFLICT)
INSERT INTO users (email, name, updated_at)
VALUES ('john@example.com', 'John', NOW())
ON CONFLICT (email) 
DO UPDATE SET 
    name = EXCLUDED.name,
    updated_at = NOW();
```

---

## Shell/Bash

```bash
#!/bin/bash

# Variables and arrays
declare -a SERVERS=("server1" "server2" "server3")
declare -A CONFIG=(
    ["host"]="localhost"
    ["port"]="8080"
)

# Functions
log() {
    local level="$1"
    local message="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message"
}

# Error handling
set -euo pipefail
trap 'log "ERROR" "Script failed on line $LINENO"' ERR

# Loops
for server in "${SERVERS[@]}"; do
    log "INFO" "Processing $server"
done

# Conditionals
if [[ -f "$FILE" ]]; then
    log "INFO" "File exists"
elif [[ -d "$FILE" ]]; then
    log "INFO" "Directory exists"
else
    log "WARN" "Not found"
fi

# String operations
STRING="Hello, World!"
echo "${STRING,,}"          # lowercase
echo "${STRING^^}"          # uppercase
echo "${STRING:0:5}"        # substring
echo "${STRING/World/User}" # replace

# Process substitution
diff <(sort file1.txt) <(sort file2.txt)

# Here documents
cat << EOF > config.yaml
server:
  host: ${CONFIG[host]}
  port: ${CONFIG[port]}
EOF

# Parallel execution
parallel_exec() {
    local -a pids=()
    for cmd in "$@"; do
        eval "$cmd" &
        pids+=($!)
    done
    for pid in "${pids[@]}"; do
        wait "$pid"
    done
}
```

Источники: Официальная документация языков, 2024-2026
