---
name: component-audit
description: >
  Audit of existing Vue components in the project. Use when reviewing Vue design
  system consistency, identifying duplicate patterns, evaluating legacy components
  (Options API), or before implementing something new.
---

# Skill: Component Audit — Vue 3

## Audit protocol

### 1. Inventory

```bash
# All SFCs
find components/ src/components/ -name "*.vue" | grep -v node_modules | sort

# Installed shadcn-vue components
ls components/ui/ 2>/dev/null || ls src/components/ui/ 2>/dev/null

# Composables
find composables/ src/composables/ -name "*.ts" 2>/dev/null | sort
```

### 2. Identify problematic patterns

```bash
# Legacy Options API (migration candidates)
grep -rl "export default {" components/ --include="*.vue" 2>/dev/null

# Without script setup
grep -rL "script setup" components/ --include="*.vue" 2>/dev/null | grep -v ui/

# Without TypeScript
grep -rl "script setup>" components/ --include="*.vue" 2>/dev/null | \
  grep -v "lang=\"ts\""

# Hardcoded hex (outside of tokens)
grep -rn "#[0-9A-Fa-f]\{6\}" components/ --include="*.vue" 2>/dev/null | \
  grep -v "ui/"

# Inline styles (outside of dynamic binding)
grep -rn "style=\"" components/ --include="*.vue" 2>/dev/null | grep -v "ui/"

# any in TypeScript
grep -rn ": any" components/ --include="*.vue" 2>/dev/null | grep -v "ui/"
```

### 3. Quality checklist per SFC

**Vue 3 Structure**
- [ ] `<script setup lang="ts">` — no Options API
- [ ] Props with typed `defineProps<Interface>()`
- [ ] Emits with typed `defineEmits<{ event: [type] }>()`
- [ ] Accepts `:class` prop for extensibility
- [ ] Uses `cn()` for conditional class composition

**Design System**
- [ ] Uses CSS tokens (no hardcoded hex)
- [ ] Spacing on 4px scale
- [ ] Variants consistent with shadcn-vue
- [ ] Dark mode functional

**States**
- [ ] Loading state with `<Skeleton>` of same dimensions
- [ ] Empty state with `<Empty>` when list/data can be empty
- [ ] Error state with `<Alert variant="destructive">`
- [ ] Success feedback via `toast()` (vue-sonner)
- [ ] Disabled state with `opacity-50 cursor-not-allowed pointer-events-none`

**Minimum accessibility**
- [ ] Correct semantic element or explicit `role`
- [ ] Accessible label for elements without visible text
- [ ] `focus-visible:ring` present and not removed

### 4. Output → `.planning/ui/component-log.md`

```markdown
## Component Audit — [date]

### Inventory
| Component | File | shadcn-vue base | Issues |
|---|---|---|---|
| UserCard | components/user/UserCard.vue | Card | No Skeleton, Options API |

### Legacy components (Options API)
[list for gradual migration]

### Duplicate patterns
- Pattern "Header with avatar + title" in 4 files → extract component

### Hardcoded tokens found
- UserCard.vue:45 — `color: #6B7280` → use `text-muted-foreground`

### Missing states
- UserList.vue — no `<Empty>` state
- OrderCard.vue — no loading skeleton

### Recommendations
1. [specific and actionable]
```

## Problematic patterns in Vue + shadcn-vue

### Options API → Composition API

```vue
<!-- ❌ Legacy Options API -->
<script>
export default {
  data() { return { count: 0 } },
  methods: { increment() { this.count++ } }
}
</script>

<!-- ✅ Composition API with script setup -->
<script setup lang="ts">
import { ref } from 'vue'
const count = ref(0)
const increment = () => count.value++
</script>
```

### Conditional classes without cn()

```vue
<!-- ❌ Template literal — does not merge Tailwind correctly -->
<div :class="`base-class ${isActive ? 'active' : ''}`" />

<!-- ✅ cn() with tailwind-merge -->
<div :class="cn('base-class', isActive && 'bg-primary text-primary-foreground')" />
```

### Missing `:class` prop

```vue
<!-- ❌ Not extensible -->
<div class="flex gap-4">

<!-- ✅ Always accept external class -->
<script setup lang="ts">
const props = defineProps<{ class?: string }>()
</script>
<template>
  <div :class="cn('flex gap-4', props.class)">
</template>
```

### Skeleton with wrong dimensions

```vue
<!-- ❌ Generic skeleton — causes layout shift -->
<Skeleton class="h-4 w-full" />  <!-- but the content is h-32 -->

<!-- ✅ Skeleton mirrors the actual content -->
<Card v-if="isLoading">
  <CardHeader>
    <Skeleton class="h-5 w-3/4" />
    <Skeleton class="h-4 w-1/2 mt-2" />
  </CardHeader>
  <CardContent>
    <Skeleton class="h-32 w-full" />
  </CardContent>
</Card>
```
