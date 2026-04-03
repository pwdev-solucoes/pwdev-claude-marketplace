# Documentation rules — pwdev-uiux

## Stack-Dependent Conventions

The conventions below are determined by the configured stack in `.planning/ui/stack.json`.
Always read the stack config before applying any convention.

### Vue 3 (shadcn-vue, primevue)
- **SFC**: always `<script setup lang="ts">` — no Options API in new code
- **Props**: `defineProps<Interface>()` with TypeScript generics
- **Emits**: `defineEmits<{ event: [PayloadType] }>()` typed
- **Composables**: `useFeatureName()` in `composables/use-feature-name.ts`
- **Components**: `PascalCase.vue` in `kebab-case/` directory

### React (shadcn/ui, untitled-ui)
- **Components**: TSX functional components with TypeScript interfaces
- **Hooks**: `useFeatureName()` in `hooks/use-feature-name.ts`
- **Props**: interface-typed with `React.FC<Props>` or direct destructuring
- **Components**: `PascalCase.tsx` in `kebab-case/` directory

### General (all stacks)
- Follow existing project conventions from `project-ui-skill.md` when available
- Use TypeScript when the stack supports it

## Naming

| Artifact | Pattern | Example |
|---|---|---|
| Component | PascalCase | `UserCard.vue` / `UserCard.tsx` |
| Feature directory | kebab-case | `user-profile/` |
| Composable/Hook | use + PascalCase | `useUserProfile.ts` |
| CSS Token | --kebab-case | `--brand-primary` |

## State files (.planning/ui/)

- Never delete — only overwrite or append
- Always include approval gate with checkboxes
- Include last update timestamp
- `project-ui-skill.md`: update with `/pwdev-uiux:scan` after structural changes

## Recommended commits per gate

```
Gate 1 approved: docs(ux): add spec for [feature]
Gate 3 completed: feat(ui): implement [ComponentName]
Gate 4 approved: fix(a11y): resolve findings for [feature]
Gate 5 completed: docs: add handoff for [feature]
```

## Suggested .gitignore

```gitignore
# pwdev-uiux state (option 1: do not version)
.planning/ui/

# pwdev-uiux state (option 2: version as living documentation)
# — do not add to .gitignore
```
