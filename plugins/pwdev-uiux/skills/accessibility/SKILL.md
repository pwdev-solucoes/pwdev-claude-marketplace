---
name: accessibility
description: >
  Accessibility auditing and remediation skill for Vue 3 + Reka UI.
  Use when reviewing components, verifying WCAG 2.1 AA, fixing ARIA issues,
  or validating keyboard navigation in Reka UI components.
---

# Skill: WCAG 2.1 AA Accessibility — Vue 3 + Reka UI

> Reka UI implements WAI-ARIA by default. The audit focuses on:
> correct usage of primitives, project-specific extensions, and Vue-specific patterns.

## What Reka UI manages automatically

✅ Do not audit — already implemented by primitives:
- Correct `role` on all components (button, dialog, menu, listbox, etc.)
- Keyboard navigation (Tab, Arrows, Enter, Space, Escape)
- `aria-expanded`, `aria-selected`, `aria-checked` on interactive components
- Focus trap in Dialog, AlertDialog, Sheet
- `aria-haspopup` on Popover, DropdownMenu triggers
- `aria-modal` on overlays

⚠️ Audit — project extensions and usages:

---

## Checklist by category

### 1. Buttons and interactive elements

```vue
<!-- ✅ Icon button — aria-label required -->
<Button size="icon" aria-label="Close dialog">
  <X class="h-4 w-4" aria-hidden="true" />
</Button>

<!-- ✅ Alternative with sr-only -->
<Button>
  <Trash2 class="h-4 w-4 mr-2" aria-hidden="true" />
  <span>Delete</span>
  <span class="sr-only">item John Smith</span>
</Button>

<!-- ❌ Icon without description -->
<Button>
  <Settings class="h-4 w-4" />
</Button>
```

### 2. Forms with vee-validate

```vue
<!-- ✅ FormField applies aria-describedby automatically -->
<FormField v-slot="{ componentField }" name="email">
  <FormItem>
    <FormLabel>Email</FormLabel>  <!-- Associated to input via automatic for/id -->
    <FormControl>
      <Input v-bind="componentField" />  <!-- id injected automatically -->
    </FormControl>
    <FormMessage />  <!-- automatic aria-live when there is an error -->
  </FormItem>
</FormField>

<!-- ❌ Input without label (even with placeholder) -->
<Input placeholder="Email" v-model="email" />

<!-- ✅ When not using FormField: explicit label -->
<label for="email-standalone">Email</label>
<Input id="email-standalone" v-model="email" />
```

### 3. Images and icons

```vue
<!-- ✅ Informative image with descriptive alt -->
<img :src="user.avatar" :alt="`Profile photo of ${user.name}`" />

<!-- ✅ Decorative image: empty alt -->
<img src="/hero-bg.png" alt="" aria-hidden="true" />

<!-- ✅ Next.js-style with Nuxt Image -->
<NuxtImg :src="photo" :alt="description" />

<!-- ✅ Standalone icon (lucide-vue-next) -->
<CheckCircle class="text-green-500" aria-label="Completed" />
<!-- or: aria-hidden + adjacent sr-only text -->
<CheckCircle aria-hidden="true" />
<span class="sr-only">Status: Completed</span>
```

### 4. Dynamic states

```vue
<!-- ✅ Loading state with aria-live -->
<div aria-live="polite" :aria-busy="isLoading">
  <template v-if="isLoading">
    <Skeleton v-for="i in 3" :key="i" class="h-8 w-full mb-2" />
  </template>
  <ul v-else>
    <li v-for="item in items" :key="item.id">{{ item.name }}</li>
  </ul>
</div>

<!-- ✅ Operation error — assertive to interrupt -->
<div v-if="error" role="alert" aria-live="assertive">
  <Alert variant="destructive">
    <AlertDescription>{{ error }}</AlertDescription>
  </Alert>
</div>

<!-- ✅ Success confirmation — polite, does not interrupt -->
<div role="status" aria-live="polite">
  <span v-if="saved" class="text-green-600">Saved successfully.</span>
</div>
```

### 5. Navigation and links

```vue
<!-- ✅ RouterLink with descriptive text -->
<RouterLink to="/product/123">View details of Product X</RouterLink>

<!-- ❌ Generic link without context -->
<RouterLink to="/product/123">Click here</RouterLink>

<!-- ✅ External link with indication -->
<a href="https://example.com" target="_blank" rel="noopener">
  External documentation
  <span class="sr-only">(opens in new tab)</span>
  <ExternalLink class="h-3 w-3 ml-1 inline" aria-hidden="true" />
</a>
```

### 6. Dialog and modals

```vue
<!-- ✅ shadcn-vue Dialog already implements correctly -->
<Dialog v-model:open="open">
  <DialogContent>
    <!-- REQUIRED: DialogTitle always present (can be sr-only) -->
    <DialogTitle>Confirm deletion</DialogTitle>
    <!-- RECOMMENDED: DialogDescription -->
    <DialogDescription>
      This action cannot be undone.
    </DialogDescription>
    <!-- Content -->
  </DialogContent>
</Dialog>

<!-- ❌ Dialog without title — screen reader does not announce context -->
<DialogContent>
  <p>Content without accessible title</p>
</DialogContent>
```

### 7. Color contrast

| Type | Minimum AA | Safe Tailwind classes |
|---|---|---|
| Normal text (< 18px regular) | 4.5:1 | text-gray-700+ on white |
| Large text (≥ 18px or 14px bold) | 3:1 | text-gray-600+ on white |
| UI elements (borders, icons) | 3:1 | border-gray-400+, text-gray-500+ |

Verify: dark mode must also pass the same criteria.

### 8. Animations and motion

```vue
<!-- ✅ Respect prefers-reduced-motion -->
<Transition
  enter-active-class="motion-safe:transition-all motion-safe:duration-200"
  leave-active-class="motion-safe:transition-all motion-safe:duration-200"
>
  <div v-if="show">Animated content</div>
</Transition>
```

In Tailwind:
```html
<!-- motion-reduce: overrides animations -->
<div class="animate-spin motion-reduce:animate-none" />
<div class="transition-all motion-reduce:transition-none" />
```

### 9. Focus

```vue
<!-- ✅ Visible focus — shadcn-vue already configures focus-visible:ring -->
<!-- Verify: not removed with outline-none without a substitute -->

<!-- ❌ Removes focus without substitute -->
<Input class="focus:outline-none" />

<!-- ✅ Custom focus ring -->
<Input class="focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none" />

<!-- ✅ Skip to content link (for long pages) -->
<a
  href="#main-content"
  class="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4"
>
  Skip to main content
</a>
```

---

## Finding severity

| Level | Criterion | Action |
|---|---|---|
| **Critical** | Blocks usage by a person with a disability | Block PHASE 4 gate |
| **High** | Significant impact — immediate fix needed | Log and recommend |
| **Medium** | Important improvement, non-blocking | Priority backlog |
| **Low** | Experience refinement | Future backlog |

---

## Testing tools

```bash
# axe-core via CLI
npx @axe-core/cli http://localhost:3000

# Playwright with axe
npm install --save-dev @axe-core/playwright

# Manual checklist
# 1. Tab through entire page — is focus always visible?
# 2. Screen reader (VoiceOver/NVDA) — is content announced correctly?
# 3. 200% zoom — does the layout hold?
# 4. High contrast (Windows) — is the interface usable?
# 5. Disable CSS — does the semantic structure make sense?
```
