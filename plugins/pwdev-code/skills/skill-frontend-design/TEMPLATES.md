# Enterprise UI Templates

Starter patterns for common enterprise interface components. All follow the design rules in `SKILL.md`.
Adapt colors, spacing, and depth strategy to your chosen design direction.

> **Usage:** These are NOT copy-paste components. They're structural references showing how to apply
> the design system. Adjust typography, colors, spacing density, and depth to match the specific
> product personality chosen in Step 2.

---

## 1. CSS Variables Foundation

Always start with a design tokens file. Here are three foundations — pick the one matching your direction:

### Cool / Professional (Stripe, Mercury)

```css
:root {
  /* Surfaces */
  --bg-app: #f8fafc;
  --bg-surface: #ffffff;
  --bg-subtle: #f1f5f9;
  --bg-hover: #e2e8f0;

  /* Text hierarchy */
  --text-primary: #0f172a;
  --text-secondary: #334155;
  --text-muted: #64748b;
  --text-faint: #94a3b8;

  /* Borders & depth */
  --border: rgba(15, 23, 42, 0.08);
  --border-strong: rgba(15, 23, 42, 0.12);
  --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.06);
  --shadow-md: 0 1px 3px rgba(15, 23, 42, 0.08), 0 2px 6px rgba(15, 23, 42, 0.04);

  /* Accent — blue for trust */
  --accent: #2563eb;
  --accent-light: #eff6ff;
  --accent-text: #1d4ed8;

  /* Semantic */
  --success: #16a34a;
  --success-light: #f0fdf4;
  --warning: #d97706;
  --warning-light: #fffbeb;
  --error: #dc2626;
  --error-light: #fef2f2;

  /* Spacing (4px grid) */
  --sp-1: 4px;
  --sp-2: 8px;
  --sp-3: 12px;
  --sp-4: 16px;
  --sp-6: 24px;
  --sp-8: 32px;

  /* Radius */
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;

  /* Typography */
  --font-sans: 'Geist', -apple-system, sans-serif;
  --font-mono: 'Geist Mono', 'SF Mono', monospace;
  --text-xs: 11px;
  --text-sm: 12px;
  --text-base: 14px;
  --text-lg: 16px;
  --text-xl: 18px;
  --text-2xl: 24px;
}
```

### Dark / Technical (Linear, Raycast)

```css
:root {
  --bg-app: #0a0a0b;
  --bg-surface: #141415;
  --bg-subtle: #1c1c1e;
  --bg-hover: #252528;

  --text-primary: #f0f0f0;
  --text-secondary: #a0a0a6;
  --text-muted: #6e6e76;
  --text-faint: #46464f;

  --border: rgba(255, 255, 255, 0.08);
  --border-strong: rgba(255, 255, 255, 0.12);
  --shadow-sm: none; /* dark mode: borders over shadows */

  --accent: #8b5cf6;
  --accent-light: rgba(139, 92, 246, 0.12);
  --accent-text: #a78bfa;

  --success: #34d399;
  --success-light: rgba(52, 211, 153, 0.1);
  --warning: #fbbf24;
  --warning-light: rgba(251, 191, 36, 0.1);
  --error: #f87171;
  --error-light: rgba(248, 113, 113, 0.1);

  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
}
```

### Warm / Approachable (Notion, Coda)

```css
:root {
  --bg-app: #faf9f7;
  --bg-surface: #ffffff;
  --bg-subtle: #f3f2ef;
  --bg-hover: #eae8e4;

  --text-primary: #1a1a1a;
  --text-secondary: #4a4a4a;
  --text-muted: #8c8c8c;
  --text-faint: #b3b3b3;

  --border: rgba(0, 0, 0, 0.06);
  --border-strong: rgba(0, 0, 0, 0.1);
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.06);

  --accent: #e16b3a;
  --accent-light: #fef3ee;
  --accent-text: #c75a2e;

  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
}
```

---

## 2. App Shell with Sidebar

The most common enterprise layout. Sidebar + header + content area.

```jsx
/* Structure reference — React + Tailwind */

function AppShell({ children }) {
  return (
    <div className="flex h-screen" style={{ background: 'var(--bg-app)' }}>
      {/* Sidebar — same bg as content, border separates */}
      <aside
        className="w-60 flex-shrink-0 flex flex-col"
        style={{
          background: 'var(--bg-app)',
          borderRight: '1px solid var(--border)',
        }}
      >
        {/* Logo / workspace */}
        <div className="p-4" style={{ borderBottom: '1px solid var(--border)' }}>
          <div className="flex items-center gap-2">
            <div
              className="w-6 h-6 rounded flex items-center justify-center text-xs font-semibold text-white"
              style={{ background: 'var(--accent)', borderRadius: 'var(--radius-sm)' }}
            >
              A
            </div>
            <span className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
              Acme Corp
            </span>
          </div>
        </div>

        {/* Nav items */}
        <nav className="flex-1 p-2 space-y-0.5">
          <NavItem icon={LayoutDashboard} label="Dashboard" active />
          <NavItem icon={Users} label="Customers" />
          <NavItem icon={FileText} label="Invoices" badge="12" />
          <NavItem icon={Settings} label="Settings" />
        </nav>

        {/* User */}
        <div className="p-3" style={{ borderTop: '1px solid var(--border)' }}>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-slate-200" />
            <div>
              <p className="text-xs font-medium" style={{ color: 'var(--text-primary)' }}>Jane Doe</p>
              <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Admin</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Page header */}
        <header
          className="h-12 flex items-center justify-between px-6 flex-shrink-0"
          style={{ borderBottom: '1px solid var(--border)' }}
        >
          <h1 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
            Dashboard
          </h1>
          <div className="flex items-center gap-2">
            {/* Action buttons go here */}
          </div>
        </header>

        {/* Scrollable content */}
        <div className="flex-1 overflow-auto p-6">
          {children}
        </div>
      </main>
    </div>
  );
}

function NavItem({ icon: Icon, label, active, badge }) {
  return (
    <button
      className="w-full flex items-center gap-2 px-2 py-1.5 rounded text-left text-sm transition-colors"
      style={{
        color: active ? 'var(--text-primary)' : 'var(--text-muted)',
        background: active ? 'var(--bg-subtle)' : 'transparent',
        fontWeight: active ? 500 : 400,
        borderRadius: 'var(--radius-sm)',
      }}
    >
      <Icon size={16} strokeWidth={active ? 2 : 1.5} />
      <span className="flex-1">{label}</span>
      {badge && (
        <span
          className="text-xs px-1.5 py-0.5 rounded-full"
          style={{
            background: 'var(--accent-light)',
            color: 'var(--accent-text)',
            fontSize: 'var(--text-xs)',
          }}
        >
          {badge}
        </span>
      )}
    </button>
  );
}
```

---

## 3. Metric Cards (varied layouts)

Each card has different internal structure but SAME surface treatment.

```jsx
/* Consistent surface wrapper */
function Card({ children, className = '' }) {
  return (
    <div
      className={`p-4 ${className}`}
      style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'var(--shadow-sm)',
      }}
    >
      {children}
    </div>
  );
}

/* KPI card — number-forward */
function KPICard({ label, value, change, trend }) {
  const isUp = trend === 'up';
  return (
    <Card>
      <p className="text-xs font-medium mb-3" style={{ color: 'var(--text-muted)' }}>{label}</p>
      <p className="text-2xl font-semibold tracking-tight" style={{
        color: 'var(--text-primary)',
        fontVariantNumeric: 'tabular-nums',
        fontFamily: 'var(--font-sans)',
        letterSpacing: '-0.02em',
      }}>
        {value}
      </p>
      <p className="text-xs mt-2" style={{
        color: isUp ? 'var(--success)' : 'var(--error)',
      }}>
        {isUp ? '↑' : '↓'} {change}
        <span style={{ color: 'var(--text-faint)', marginLeft: 4 }}>vs last month</span>
      </p>
    </Card>
  );
}

/* Progress card — with bar */
function ProgressCard({ label, current, total, unit }) {
  const pct = Math.round((current / total) * 100);
  return (
    <Card>
      <div className="flex items-center justify-between mb-3">
        <p className="text-xs font-medium" style={{ color: 'var(--text-muted)' }}>{label}</p>
        <p className="text-xs font-mono" style={{ color: 'var(--text-faint)' }}>{pct}%</p>
      </div>
      <div className="h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--bg-subtle)' }}>
        <div
          className="h-full rounded-full transition-all"
          style={{ width: `${pct}%`, background: 'var(--accent)' }}
        />
      </div>
      <p className="text-sm mt-3" style={{ color: 'var(--text-primary)' }}>
        <span className="font-semibold font-mono" style={{ fontVariantNumeric: 'tabular-nums' }}>
          {current.toLocaleString()}
        </span>
        <span style={{ color: 'var(--text-faint)' }}> / {total.toLocaleString()} {unit}</span>
      </p>
    </Card>
  );
}

/* List card — with avatar stack */
function RecentActivityCard({ items }) {
  return (
    <Card className="p-0">
      <div className="px-4 pt-4 pb-3">
        <p className="text-xs font-medium" style={{ color: 'var(--text-muted)' }}>Recent Activity</p>
      </div>
      <div>
        {items.map((item, i) => (
          <div
            key={i}
            className="flex items-center gap-3 px-4 py-2.5"
            style={{ borderTop: '1px solid var(--border)' }}
          >
            <div
              className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-medium"
              style={{ background: 'var(--bg-subtle)', color: 'var(--text-muted)' }}
            >
              {item.initials}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm truncate" style={{ color: 'var(--text-primary)' }}>{item.action}</p>
              <p className="text-xs" style={{ color: 'var(--text-faint)' }}>{item.time}</p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
```

---

## 4. Data Table

```jsx
function DataTable({ columns, rows }) {
  return (
    <div
      className="overflow-hidden"
      style={{
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        background: 'var(--bg-surface)',
      }}
    >
      <table className="w-full text-sm">
        <thead>
          <tr style={{ borderBottom: '1px solid var(--border)' }}>
            {columns.map((col) => (
              <th
                key={col.key}
                className="text-left px-4 py-2.5 text-xs font-medium"
                style={{
                  color: 'var(--text-muted)',
                  background: 'var(--bg-subtle)',
                  letterSpacing: '0.02em',
                }}
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr
              key={i}
              className="transition-colors"
              style={{
                borderBottom: i < rows.length - 1 ? '1px solid var(--border)' : 'none',
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-subtle)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
            >
              {columns.map((col) => (
                <td
                  key={col.key}
                  className="px-4 py-2.5"
                  style={{
                    color: col.mono ? 'var(--text-secondary)' : 'var(--text-primary)',
                    fontFamily: col.mono ? 'var(--font-mono)' : 'inherit',
                    fontVariantNumeric: col.mono ? 'tabular-nums' : 'normal',
                    fontSize: col.mono ? 'var(--text-sm)' : 'var(--text-base)',
                  }}
                >
                  {row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

---

## 5. Filter Bar

Isolated controls with container treatment. No native selects.

```jsx
function FilterBar({ filters, onFilterChange }) {
  return (
    <div className="flex items-center gap-2 mb-4">
      {/* Custom select trigger */}
      <button
        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm transition-colors"
        style={{
          whiteSpace: 'nowrap',
          display: 'inline-flex',      /* MUST: keeps text + icon on same row */
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius-md)',
          background: 'var(--bg-surface)',
          color: 'var(--text-secondary)',
        }}
      >
        <span>Status: All</span>
        <ChevronDown size={14} style={{ color: 'var(--text-faint)' }} />
      </button>

      {/* Search input */}
      <div
        className="flex items-center gap-2 px-3 py-1.5 flex-1 max-w-xs"
        style={{
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius-md)',
          background: 'var(--bg-surface)',
        }}
      >
        <Search size={14} style={{ color: 'var(--text-faint)' }} />
        <input
          type="text"
          placeholder="Search..."
          className="bg-transparent border-none outline-none text-sm flex-1"
          style={{ color: 'var(--text-primary)' }}
        />
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Action button */}
      <button
        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-white transition-colors"
        style={{
          background: 'var(--accent)',
          borderRadius: 'var(--radius-md)',
          border: 'none',
        }}
      >
        <Plus size={14} />
        <span>New Item</span>
      </button>
    </div>
  );
}
```

---

## 6. Status Badge

Typography-driven, minimal color usage.

```jsx
function StatusBadge({ status }) {
  const styles = {
    active:  { bg: 'var(--success-light)', color: 'var(--success)', dot: 'var(--success)' },
    pending: { bg: 'var(--warning-light)', color: 'var(--warning)', dot: 'var(--warning)' },
    error:   { bg: 'var(--error-light)',   color: 'var(--error)',   dot: 'var(--error)' },
    draft:   { bg: 'var(--bg-subtle)',     color: 'var(--text-muted)', dot: 'var(--text-faint)' },
  };

  const s = styles[status] || styles.draft;

  return (
    <span
      className="inline-flex items-center gap-1.5 px-2 py-0.5 text-xs font-medium rounded-full"
      style={{ background: s.bg, color: s.color }}
    >
      <span
        className="w-1.5 h-1.5 rounded-full"
        style={{ background: s.dot }}
      />
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}
```

---

## 7. Empty State

Even empty states deserve design attention.

```jsx
function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div
        className="w-10 h-10 rounded-lg flex items-center justify-center mb-3"
        style={{ background: 'var(--bg-subtle)' }}
      >
        <Icon size={20} style={{ color: 'var(--text-faint)' }} />
      </div>
      <h3 className="text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
        {title}
      </h3>
      <p className="text-sm max-w-xs" style={{ color: 'var(--text-muted)' }}>
        {description}
      </p>
      {action && (
        <button
          className="mt-4 inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-white"
          style={{ background: 'var(--accent)', borderRadius: 'var(--radius-md)' }}
        >
          {action}
        </button>
      )}
    </div>
  );
}
```

---

## Notes on Usage

- **These templates use JSX + Tailwind + Lucide as a reference syntax.** Adapt to your project's stack (Vue, Svelte, HTML) and component library as defined in SPEC.md section 1.
- **CSS variables are the source of truth.** Tailwind classes handle layout, variables handle design tokens.
- **Start with the App Shell**, then compose components inside it. Never render isolated components.
- **Vary card internals.** The `Card` wrapper stays the same; what goes inside changes per use case.
- **Data always in monospace.** Any number, ID, date, code should use `var(--font-mono)` + `tabular-nums`.
- **Check CLAUDE.md** for project-specific conventions before implementing any template.
