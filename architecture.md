# AgentLens Architecture

```
┌────────────┐
│ AI Agent   │
└─────┬──────┘
      │
      ▼
┌────────────────────┐
│ AgentLens SDK      │
│ (@trace decorator) │
└─────┬──────────────┘
      │
      ▼
┌────────────────────┐
│ Trace Store        │
│ SQLite             │
└─────┬──────────────┘
      │
      ▼
┌────────────────────┐
│ Evaluation Engine  │
│ • Rule Checks      │
│ • DeepSeek Judge   │
└─────┬──────────────┘
      │
      ▼
┌────────────────────┐
│ Dashboard + CLI    │
└─────┬──────────────┘
      │
      ▼
┌────────────────────┐
│ GitHub Actions CI  │
└────────────────────┘
```

## Data Flow

```
Agent
    ↓
SDK (@trace)
    ↓
SQLite Trace Store
    ↓
Evaluation Engine
    ↓
Dashboard / CLI
    ↓
CI Quality Gate
```