---
name: ui-best-practices
description: >
  Canonical UI/UX best practices ruleset with 14 sections and 70+ rules prioritized
  P0–P3. Use when implementing, reviewing, or auditing UI components. P0 rules are
  mandatory — violations are bugs. All rules reference tokens from ui-theme-reference.
---

# Critical Instructions

You will receive a series of UI/UX improvement suggestions to apply to the product we are developing.

**Your workflow:**
1. Read all rules below and evaluate which ones apply to our current context
2. Confirm with me before applying changes that affect backend, performance, security, or shared infrastructure
3. Proceed one by one — do not batch-apply without alignment
4. Break work into stages if needed, but cover all rules across stages

**Priority levels used in this document:**
- **P0 — Mandatory**: violations are bugs. Always apply.
- **P1 — Strong default**: apply unless there is an explicit, documented reason not to.
- **P2 — Recommended**: apply when context allows; skip with justification.
- **P3 — Contextual**: evaluate case by case; most relevant for specific product types.

**Theme reference:** all token values (colors, sizes, spacing, shadows) are defined in the `ui-theme-reference` skill. Rules below reference tokens as `theme.<section>.<token>` — never hardcode raw values in components.

**Related plugin commands:**
- `/pwdev-uiux:theme` — create or update the theme token system
- `/pwdev-uiux:scan` — audit existing UI against these rules
- `/pwdev-uiux:review` — run accessibility + UX review

---

## 1. Visual Foundation

### 1.1 Light and Dark Mode `P0`
Always support both light and dark mode. Default to the user's OS preference via `prefers-color-scheme`. Users who have their device in dark mode must enter with the correct experience without manual configuration.

Both modes must be defined in the theme — see `theme.colors.surfaces` for the full token set.

### 1.2 Semantic Color Tokens `P0`
Never use hardcoded hex values in components. All colors must come from semantic tokens defined in `theme.colors`:

- **Surfaces**: `--background`, `--card`, `--popover`, `--muted`
- **Text**: `--foreground`, `--muted-foreground`
- **Interactive**: `--primary`, `--secondary`, `--accent`
- **Feedback**: `--success`, `--warning`, `--destructive`, `--info`
- **Structure**: `--border`, `--input`, `--ring`

Every foreground token has a paired background token. Components use both: `bg-primary text-primary-foreground`.

### 1.3 Reserved Semantic Colors `P0`
Green, orange, and red carry universal meaning across all interfaces:

| Color | Meaning | Token |
|-------|---------|-------|
| Green | Positive / success / complete | `--success` |
| Orange | Caution / attention needed | `--warning` |
| Red | Error / danger / destructive | `--destructive` |

Never repurpose these for decoration, categories, or branding. For data visualization, use the dedicated `theme.colors.chart-palette`.

### 1.4 Vector Icons Only `P1`
Use SVG icons from a consistent library (Lucide, Heroicons, Phosphor) instead of emojis. Emojis render differently across OS and break visual consistency. Choose one icon library and use it throughout the entire product.

### 1.5 Flat Visual Style `P1`
Prefer solid colors and flat surfaces with minimal, soft shadows. Avoid gradients on buttons, backgrounds, text, or dividers — they age quickly and create visual noise. Use `theme.shadows` tokens for elevation instead.

**Exception:** subtle gradients on hero/marketing sections are acceptable if the design system explicitly allows it.

### 1.6 Consistent Border Radius `P1`
Border radius communicates brand personality. Define `theme.radius.--radius` once and derive all variants from it:

| Brand Style | Base radius |
|-------------|-------------|
| Modern / trendy | `12–16px` |
| Neutral / corporate | `8px` (safe default) |
| Enterprise / dense | `4px` |
| Sharp / editorial | `0–2px` |

All elements (buttons, inputs, cards, modals) must use the same radius scale. See `theme.border-radius`.

### 1.7 Shadow System `P1`
Use shadows only from `theme.shadows` — black with opacity between 5% and 12% for light mode:

| Level | Usage |
|-------|-------|
| `--shadow-xs` | Inputs, badges (subtle lift) |
| `--shadow-sm` | Cards at rest |
| `--shadow-md` | Elevated cards, dropdowns |
| `--shadow-lg` | Modals, popovers |
| `--shadow-xl` | Command palette, overlays |

Never use colored shadows or opacity above 12%.

---

## 2. Typography

### 2.1 Sans-Serif Font Stack `P1`
For SaaS interfaces, use a clean sans-serif font. Default: **Inter** (free, universal, excellent readability). Alternatives: Roboto, Manrope, Segoe UI, Helvetica Neue.

Define in `theme.typography.--font-sans`. Use `theme.typography.--font-mono` for code blocks.

### 2.2 Minimum Font Size: 12px `P0`
Default body text: `14px` (`theme.typography.--text-sm`). Never use fonts smaller than `12px` (`theme.typography.--text-xs`). The 12px minimum is an accessibility requirement, allowed only for footnotes, captions, and very secondary labels.

### 2.3 Progressive Type Scale `P0`
Adjacent text elements must not skip more than 2 steps in the type scale. Jumping from `30px` directly to `14px` creates jarring contrast.

Use the scale defined in `theme.typography.type-scale`: `36 → 30 → 24 → 20 → 18 → 16 → 14 → 12`. Each transition should feel gradual.

### 2.4 Consistent Font Weights `P2`
Use no more than 3–4 font weights across the interface. Stick to the scale in `theme.typography.font-weights`: normal (400), medium (500), semibold (600), bold (700).

---

## 3. Layout & Spacing

### 3.1 4px Spacing Grid `P0`
All spacing values must be multiples of 4px. Use tokens from `theme.spacing`. Arbitrary values like `13px` or `37px` break rhythm and create visual inconsistency.

### 3.2 Proportional Card Padding `P1`
Card padding should range from `16px` to `24px` (see `theme.spacing.card-padding-rule`). More important cards get larger padding. Never exceed `32px` — excessive padding makes cards feel empty.

### 3.3 Homogeneous Alignment `P1`
All elements on a page must follow the same alignment logic. If titles and inputs are left-aligned, buttons are left-aligned. If everything is centered, buttons are centered. Never mix alignments without clear visual intent.

### 3.4 Button Sizing `P1`
In wide forms (700–1000px), buttons should have content-adjusted width, not `width: 100%`. Maximum button width: `theme.sizing.--max-w-button` (400px). In narrow mobile forms, full-width buttons are acceptable.

### 3.5 Input and Button Height Parity `P0`
Buttons and inputs must share the same height: `theme.sizing.--height-input` (40px). This ensures visual harmony when placed side by side in forms. Use `--height-button-sm` (32px) only in compact contexts (tables, toolbars).

### 3.6 Textarea Proportional Height `P2`
Match textarea height to expected content length. A tagline field: ~2 rows. A description field: ~4–5 rows. A feedback field: ~6–8 rows. Always enable auto-resize. See `theme.sizing.textarea-height`.

### 3.7 Form Width Influences Perception `P2`
Narrow forms feel quick and simple — use during onboarding. Wide forms feel like more effort — useful for discouraging cancellation flows. Max form width: `theme.sizing.--max-w-form` (560px).

---

## 4. Button Hierarchy

### 4.1 Action Weight Mapping `P0`
Every button must visually reflect its action weight:

| Level | Style | Examples |
|-------|-------|----------|
| **Primary** | `bg-primary text-primary-foreground` | Save, Confirm, Submit |
| **Secondary** | `border-border` outline, no fill | Cancel, Dismiss |
| **Tertiary** | Text only, no border | Go back, Skip, Learn more |
| **Destructive** | Same hierarchy levels, using `--destructive` | Delete, Remove, Revoke |

Never give two buttons on the same view the same visual weight unless they are truly equal options.

### 4.2 Unambiguous Button Labels `P0`
In confirmation dialogs, button text must describe the specific action — not generic "Confirm" / "Cancel". If the destructive action is "Cancel subscription", the buttons should read **"Go back"** and **"Yes, cancel subscription"**.

---

## 5. Navigation

### 5.1 Home as Control Center `P1`
The home page must be the user's operational hub: shortcuts to frequent actions, key metrics/insights, and product updates. The user should never need to "hunt" for what to do next.

### 5.2 Menu Shows Only the Operational Routine `P1`
The main menu contains only actions the user performs every session. Infrequent actions (settings, integrations, billing, support) go in secondary menus — the avatar dropdown or a "More" section.

### 5.3 Global Search (Cmd+K) `P2`
Implement a universal search (actions, pages, data) accessible via `Cmd+K` / `Ctrl+K`. Power users navigate significantly faster with this pattern. Follows `theme.z-index.--z-command` for layering.

### 5.4 Sidebar for 4+ Items, Top Bar for Fewer `P1`
- **4+ navigation items**: sidebar (more vertical space, supports grouping, always visible)
- **Up to 4 items**: top bar (cleaner, full content width)

### 5.5 Separate Routine vs. Occasional `P1`
If the menu has many items, split by frequency: daily-use items at the top, always visible. Occasional items (settings, integrations) grouped at the bottom or in a submenu.

### 5.6 Group Items into Sections and Submenus `P1`
When the menu has many items, divide them into logical sections with clear titles or collapsible submenus. Instead of processing 12 loose items, the user sees 3 organized groups. Use visual separators or section labels to reduce cognitive load.

### 5.7 Active Item Indicator `P0`
The currently active menu item must be visually distinct: highlight color, differentiated background, colored sidebar accent, or a combination. The user must always know where they are.

### 5.8 Position Communicates Hierarchy `P2`
In top menus: primary items left, secondary items right. In sidebars: primary items top, secondary items bottom. Spatial position is an implicit priority signal.

### 5.9 Main CTA in the Menu `P2`
If there is a high-frequency action (e.g., "New project", "Create task"), add a CTA button directly in the navigation. Eliminates extra clicks to reach the most important action.

### 5.10 Menu Order: Process or Frequency `P2`
Items follow either process order (Register → Configure → Execute → Analyze) or frequency order (most used first). Pick one logic and apply consistently.

### 5.11 Mobile Navigation `P1`
- **Up to 4–5 functions**: bottom bar (thumb-reachable)
- **Complex menus**: hamburger in top bar, aligned right
- Maximum 4 visible items on mobile — group the rest under "More"

See `theme.breakpoints` for responsive trigger points.

---

## 6. Tabs

### 6.1 Always Define a Default Tab `P0`
When a page has tabs, one must always be pre-selected. Never show an empty tab state on load. The default tab is the most relevant or the first in the flow.

### 6.2 Few Tabs with Short Content = Sections `P2`
If you have only 2–3 tabs with short content each, consider removing tabs and showing everything as scrollable sections on one page. Reduces clicks, gives a complete overview.

### 6.3 Constant Tab Switching = Merge `P2`
If users constantly switch between tabs to compare data, that content belongs on the same page. "Back and forth" tab navigation signals the need for consolidation.

### 6.4 Pending Badges on Tabs `P1`
Show badges, numbers, or dot indicators on tabs that have pending items or status changes. The user should see that a tab needs attention without opening it.

### 6.5 6+ Tabs = Vertical Tabs or Submenu `P2`
More than 6 horizontal tabs causes overflow and readability issues. Switch to vertical tabs or a side submenu.

### 6.6 Object Actions vs. Tab Actions `P1`
Actions affecting the whole object (save, delete, archive) belong in the page header — outside tabs. Actions specific to one tab (add member, new comment) stay inside that tab. Mixing the two confuses users.

---

## 7. Data Interactions

### 7.1 Listings Show the Minimum `P1`
Tables and card lists should show just enough to identify the object and decide whether to open it. Save details for the internal view. Over-displaying data clutters the interface and slows scanning.

### 7.2 Table Default, Cards for Visual Content `P1`
Tables are denser, more scannable, and more efficient — use as default. Use cards when visual identification matters (products with photos, templates with previews, posts with thumbnails).

### 7.3 Quick Actions in Listings `P1`
Include 2–3 frequent actions directly in the listing (duplicate, delete, publish). Prevents opening each item just to perform a simple action. For more actions, use a kebab menu (three dots).

### 7.4 Many Actions = Overflow Menu `P1`
When an object has many available actions, showing all of them clutters the interface. Surface the 2–3 most frequent actions inline and group the rest in a kebab menu (three dots). The interface stays clean without losing functionality.

### 7.5 Complex Objects Need Tabs or Sections `P1`
When an object has many data fields and relationships, do not dump everything on a single scrollable page. Use tabs or well-defined sections to organize information by context — e.g., "General", "History", "Settings". This reduces cognitive load and improves navigation.

### 7.6 Place the Create Button Where Most Visible `P1`
The "create new" button can live in the page header, sidebar, or between cards. What matters most is that it is visible and accessible in the context where the user needs it. Never bury the primary creation action.

### 7.7 Click Behavior Proportional to Data `P1`
| Data volume | Open with |
|-------------|-----------|
| 3–5 fields | Modal / popup |
| Intermediate | Drawer (side panel) |
| Complex / many relations | Dedicated page |

A full page for 3 fields is wasteful; a popup for 20 fields is suffocating.

### 7.8 Creation: Popup First, Page Later `P2`
If an object has many fields but few are required, start with a popup asking only the essentials (name, type). After creation, redirect to the full detail page. Reduces initial friction.

### 7.9 Auto-Save When Safe `P2`
Save automatically when edits are local and have no side effects. Show subtle feedback: "Saved" / "Saving...". When edits trigger emails, affect integrations, or impact other users, require an explicit "Save changes" button.

### 7.10 Empty State = Guidance `P0`
Never show a blank table. Empty states must include: an illustration or visual, a clear explanation of what belongs here, and a prominent CTA ("Create your first project"). Optionally: a short video or link to docs.

---

## 8. Deletion & Destructive Actions

### 8.1 Confirm Before Deleting `P0`
Always show a confirmation dialog before deletion. State the consequences clearly: "This will permanently remove the project and 12 associated tasks."

### 8.2 Critical Deletion Requires Extra Friction `P0`
For high-impact deletions (account, workspace, irrecoverable data), require the user to type the object name or a confirmation phrase. Protects against accidental clicks.

### 8.3 Simple Objects Can Skip Confirmation `P2`
Easy-to-recreate, non-critical items (drafts, tags, saved filters) can be deleted directly — but always offer an undo option (toast with "Undo" button for 5–10 seconds).

### 8.4 Allow Undoing Deletions `P1`
Whenever possible, support undo via:
- A toast notification with "Undo" button (5–10 seconds), or
- A trash/archive where deleted items remain recoverable for a defined period (e.g., 30 days)

---

## 9. Access & Onboarding

### 9.1 Login Screen Shows Updates `P2`
The login screen is visited by every returning user. Use a sidebar column to show product news, feature launches, and improvements. Transforms a "dead" moment into a communication channel.

### 9.2 Redirect to Intended Destination `P0`
When the user is redirected to login, preserve the original URL via `?redirect=/path`. After authentication, redirect there — never to a generic dashboard.

### 9.3 Signup Screen Sells the Product `P2`
While the user fills the signup form, use the remaining space for screenshots, testimonials, and key benefits. Reaffirms the decision and reduces abandonment.

### 9.4 Multi-Step Signup `P1`
Step 1: email + password only (minimum to not lose the lead). Subsequent steps: name, company, phone. If the user abandons at step 2, you still have their email to follow up.

### 9.5 Input Masks `P1`
Apply automatic formatting masks to fields with predictable formats: phone, CPF, CNPJ, ZIP code, credit card. Reduces errors, speeds up input, conveys professionalism.

### 9.6 Social Login `P1`
Offer at minimum Google login for B2B SaaS. Add GitHub, Microsoft, or Apple depending on the niche. Always maintain email/password fallback.

### 9.7 No Password Confirmation Field `P2`
Replace the "confirm password" field with a show/hide toggle button. Less friction, more effective, works well with password managers.

### 9.8 Onboarding Wizard `P1`
Guide new users through essential setup in a step-by-step wizard with a progress bar. The goal: reach the Aha Moment — when the user first perceives real value — as quickly as possible.

### 9.9 Pre-Populate Fields `P2`
Deduce and auto-fill information whenever possible. The user reviews and confirms instead of writing from scratch. Passive confirmation is easier than active input.

### 9.10 Demo Data on First Launch `P2`
New users who see an empty interface don't know where to start. Seed realistic demo data (projects, tasks, reports marked "demo") so the tool feels alive from the first second.

### 9.11 Suggest Upgrade on Cheapest Plan `P3`
When the user picks the cheapest plan, show a subtle popup with 2–3 benefits of the next tier and the price difference. Not aggressive — informational. Many users upgrade at this point.

### 9.12 Gamification for Retention `P3`
Identify behaviors correlated with lower churn. Reward those behaviors with points, badges, and levels. Gamification is a retention strategy, not a decoration.

### 9.13 Short Demo Videos (30s–2min) `P3`
Record brief, focused videos showing exactly how each key feature works. Place them near the feature in the UI — not buried in a help center.

### 9.14 Educational Message Sequences `P3`
Automate onboarding messages (email or in-app): Day 1 welcome, Day 3 first integration, Day 7 advanced tip, Day 14 hidden features. Education reduces churn.

### 9.15 Human Face in Demo Videos `P3`
Videos featuring a real person create a human connection with the user. Beyond improving content retention, they convey the feeling of personalized support behind the tool. Include a visible webcam overlay in screencasts when possible.

---

## 10. Forms & Long Flows

### 10.1 Break Into Short Steps `P1`
Long forms scare users. Break into focused steps with clear objectives. Progress bars and step labels reduce anxiety. Each step should be completable in under 60 seconds.

### 10.2 Name Steps by Objective `P1`
Label each step with its purpose: "Personal Data", "Address", "Payment". Avoid generic labels like "Step 2" or "50% complete".

### 10.3 Field Height Sets Expectation `P2`
Match input field height to the expected content length. A name field should be slim; a feedback or description field should be taller to encourage longer responses. Tall fields signal "write more here", short fields signal "keep it brief". Always enable auto-resize for textareas.

### 10.4 Tooltips on Complex Fields `P1`
When a field requires reasoning or is easily misunderstood, add a `?` tooltip next to the label. Prevents abandonment without cluttering the UI with visible help text.

### 10.5 Show or Hide Progress Strategically `P2`
- **Transparency priority**: show progress (Step X of Y) with labeled stages
- **Conversion priority**: consider hiding progress to prevent "there's still a lot left" abandonment

### 10.6 Real-Time Preview `P2`
When the flow builds something visual (a site, a card, a document), show a live preview as the user progresses. Concrete progress motivates completion.

### 10.7 Review Step in Critical Flows `P0`
In irreversible flows (payment, contract, permanent registration), add a final review step. Show all data in summary format with "Edit" links next to each section.

### 10.8 Confirmation via External Channel `P2`
After critical actions (payment, contract, booking), send a summary via email, WhatsApp, or SMS. Reinforces trust and serves as a receipt.

---

## 11. Reports & Dashboards

### 11.1 Dashboards from Real User Needs `P1`
Interview users to understand which metrics matter. The dashboard is a living artifact — collect feedback continuously and iterate. Never define dashboard content based solely on team assumptions.

### 11.2 Presentation Hierarchy `P1`
Most important content at top-left. Follow this order: KPIs first → simple charts → complex charts → tables/lists.

### 11.3 Avoid Pie Charts `P1`
Humans struggle to compare angles and areas. Bar charts provide clearer, more precise readings of the same data in virtually all cases. Use pie charts only when showing a single dominant proportion (e.g., 92% vs 8%).

### 11.4 Chart Type by Data Nature `P1`
- **Continuous data** (revenue over time, traffic trends): line chart
- **Discrete data** (sales by plan, tickets by category): bar chart
- **Long X-axis labels**: horizontal bar chart

### 11.5 The 3-Second Rule `P1`
If a chart takes more than 3 seconds to understand, it is too complex. Avoid dual Y-axes, too many overlapping series, or logarithmic scales. Simplify or split into smaller charts.

### 11.6 Highlight One Series, Gray the Rest `P2`
To draw attention to a specific data series, use a highlight color for that series and `theme.colors.--chart-muted` for all others. The eye goes directly to the highlighted data.

### 11.7 Remove Y-Axis for Few Data Points `P2`
When a chart has 12 or fewer points, remove the Y-axis and label values directly on each bar or point. Reduces noise and enables immediate reading.

### 11.8 KPIs with Comparison Reference `P1`
An isolated number says little. Accompany KPIs with: period-over-period comparison, industry benchmark, or long-term average. Add directional arrows and color from `theme.colors.feedback` for instant reading.

### 11.9 Chart Visual Consistency `P1`
Charts must use the product's font family, minimum `12px` labels, and the primary color for emphasis. Charts should look like part of the product — not a foreign element.

### 11.10 Practical Period Filters `P2`
Offer shortcut filters: "This week", "Last week", "This month", "Last 30 days", plus a custom date range picker.

### 11.11 Value-Added Metrics `P3`
If measurable: show "time saved", "cost reduced", "revenue added" — the concrete impact of your product. When users see tangible ROI, canceling becomes much harder.

---

## 12. Errors & Validation

### 12.1 Real-Time Field Validation `P0`
Validate on blur or on input — not only on form submit. Users should correct errors immediately, not discover them all at once at the end.

### 12.2 Visible Rules Checklist `P1`
For fields with rules (min length, special characters), show a checklist with real-time visual feedback (green check per rule met) before the user starts typing.

### 12.3 Always Report Backend Errors `P0`
Never leave the UI silent on server errors. Display a clear, visible message in plain language. Suggest a resolution when possible ("try again" or "contact support"). No raw error codes ("Error 500").

### 12.4 Proactive Support on Critical Errors `P1`
On critical failures (payment error, data loss, broken integration), proactively open the support chat with a pre-filled message describing the problem. The user just clicks "Send".

### 12.5 Auto-Correct Obvious Intent `P2`
If the user's intent is unambiguous, fix it automatically instead of showing an error. Classic examples: prepend `https://` to bare domains, format phone numbers with masks, strip extra spaces.

---

## 13. Performance & Loading

### 13.1 Compress Images, Use WebP `P0`
Always compress images before serving. Prefer `.webp` — significantly lighter than PNG/JPG at equivalent quality. Heavy images are the #1 perceived performance killer.

### 13.2 Paginate Long Lists `P0`
Lists with 20+ items must be paginated or virtualized. Beyond performance concerns, unpaginated lists harm navigation and scanning. Keep the interface fast and controllable.

### 13.3 Skeleton Loading Over Spinners `P1`
Use skeleton placeholders (gray shapes mimicking the real layout) instead of generic spinners. The brain starts processing the page structure before content arrives, reducing perceived wait time.

### 13.4 Visual Feedback on Bulk Actions `P1`
For batch operations (100+ items), show: progress bar, counter ("142 of 300"), percentage, and estimated time remaining. Never show only "Please wait...".

---

## 14. Motion & Focus

### 14.1 Respect Reduced Motion `P0`
Always honor `prefers-reduced-motion: reduce`. Disable or minimize all animations and transitions for users who request it. See `theme.motion` for duration tokens.

### 14.2 Consistent Animation Durations `P2`
Use duration tokens from `theme.motion`:
- Hover/toggle: `--duration-fast` (150ms)
- Dropdown/tooltip: `--duration-normal` (200ms)
- Drawer/modal: `--duration-slow` (300ms)

### 14.3 Visible Focus Indicators `P0`
All interactive elements must show a visible focus ring when navigated via keyboard. Use `theme.focus` tokens: `--ring-width` (2px), `--ring-offset` (2px), `--ring-color`.

Never remove `:focus-visible` outlines without providing a custom alternative.

### 14.4 Minimum Touch Target `P0`
All tappable elements must be at least `44x44px` on touch devices (WCAG 2.5.8). This applies to buttons, links, checkboxes, and icon actions. The visual size can be smaller if the tap area is padded.

### 14.5 Z-Index Management `P1`
Use the managed scale from `theme.z-index`. Never use arbitrary z-index values (999, 99999). Every layer has a defined token — dropdown (10), sticky (20), drawer (30), modal (40), toast (60), command palette (70).
