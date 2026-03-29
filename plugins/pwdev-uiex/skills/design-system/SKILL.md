---
name: design-system
description: >
  Documentation, standardization, and governance of the Vue + shadcn-vue design system.
  Use when creating component documentation, auditing consistency, defining naming
  conventions, or generating usage guides for the team.
---

# Skill: Design System — Vue 3 + shadcn-vue

## Recommended documentation structure

```
docs/
  design-system/
    foundations/
      colors.md         # Semantic tokens and palette
      typography.md     # Typographic scale
      spacing.md        # Grid and spacing
      motion.md         # Vue transitions and animations
    components/
      [ComponentName].md
    patterns/
      forms.md          # vee-validate + Zod + shadcn-vue
      navigation.md     # RouterLink + NavigationMenu
      feedback.md       # toast (vue-sonner), Alert, Dialog
      empty-states.md   # Empty component patterns
      loading.md        # Skeleton patterns
    decisions/
      adr-001.md        # Architecture Decision Records
```

## Vue component documentation template

```markdown
# ComponentName

## When to use
[Correct use case]

## When NOT to use
[Alternatives and when another component is better]

## Installation
\`\`\`bash
npx shadcn-vue@latest add [component-name]
\`\`\`

## Props
| Prop | Type | Default | Description |
|---|---|---|---|
| `variant` | `'default' \| 'outline'` | `'default'` | Visual style |
| `class` | `string` | `''` | Additional classes via cn() |

## Emits
| Event | Payload | Description |
|---|---|---|
| `update:modelValue` | `string` | New selected value |

## Examples

### Basic usage
\`\`\`vue
<ComponentName :label="'Action'" @click="handleClick" />
\`\`\`

### With loading state
\`\`\`vue
<ComponentName :loading="isLoading" />
\`\`\`

## Accessibility
- Reka UI manages: [list]
- Project must ensure: [list]

## Pattern with vee-validate (when form)
\`\`\`vue
<FormField v-slot="{ componentField }" name="field">
  <FormItem>
    <FormLabel>Label</FormLabel>
    <FormControl>
      <ComponentName v-bind="componentField" />
    </FormControl>
    <FormMessage />
  </FormItem>
</FormField>
\`\`\`

## Gotchas
- [gotcha specific to this component]
```

## Required Vue patterns to document

### Form pattern with vee-validate + Zod

```markdown
## Form Pattern

### Stack
- vee-validate 4.x + @vee-validate/zod + Zod

### Standard structure
1. Zod schema with localized messages
2. useForm({ validationSchema: toTypedSchema(schema) })
3. FormField + FormItem + FormLabel + FormControl + FormMessage
4. Button with :disabled="form.isSubmitting.value" + Spinner
5. toast.success/error after submit

### Alternative without vee-validate
- Field + FieldGroup + FieldLabel + FieldDescription + FieldError
- For simple forms without complex validation
```

### Empty states pattern

```vue
<Empty>
  <EmptyHeader>
    <EmptyTitle>No [item] found</EmptyTitle>
    <EmptyDescription>
      [Instruction on what the user can do]
    </EmptyDescription>
  </EmptyHeader>
  <EmptyContent>
    <Button @click="primaryAction">Primary action</Button>
  </EmptyContent>
</Empty>
```

### Loading states pattern

```vue
<!-- Rule: Skeleton must have the SAME dimensions as the actual content -->
<template>
  <div v-if="isLoading" aria-live="polite" aria-busy="true">
    <!-- Mirrors the structure of the actual content -->
    <Skeleton class="h-[exact dimension of the element]" />
  </div>
  <div v-else>
    <!-- Actual content -->
  </div>
</template>
```

### User feedback pattern

```markdown
## Feedback hierarchy

1. **Inline** (FormMessage, FieldError) — field validation errors
2. **Toast** (vue-sonner) — confirmations and async operation errors
3. **Alert** — persistent on-page warnings, not dismissible
4. **AlertDialog** — confirmation of destructive actions (always use)
5. **Dialog** — complex actions requiring additional input

### Never:
- Toast for form errors (use FormMessage)
- Alert for temporary notifications (use Toast)
- Dialog for simple confirmations (use AlertDialog)
```

## DS consistency checklist

Run before each release:
- [ ] New components documented in `docs/design-system/components/`
- [ ] No hardcoded values outside CSS tokens
- [ ] `<script setup lang="ts">` in all new SFCs
- [ ] Dark mode tested on all new components
- [ ] Relevant decisions in `docs/design-system/decisions/`
- [ ] `<Empty>` state in all components that list data
- [ ] `<Skeleton>` with correct dimensions in all loading states

## Conventional commits for DS

```bash
feat(ds): add UserCard component
fix(ds): correct Skeleton dimensions in OrderList
docs(ds): document Button component variants
chore(ds): update shadcn-vue components to latest
```
