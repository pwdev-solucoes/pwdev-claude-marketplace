# Documentation rules — pwdev-uiux

## Vue 3 Conventions

- **SFC**: always `<script setup lang="ts">` — no Options API in new code
- **Props**: `defineProps<Interface>()` with TypeScript generics
- **Emits**: `defineEmits<{ event: [PayloadType] }>()` typed
- **Composables**: `useFeatureName()` in `composables/use-feature-name.ts`
- **Components**: `PascalCase.vue` in `kebab-case/` directory

## Naming

| Artifact | Pattern | Example |
|---|---|---|
| Vue Component | PascalCase | `UserCard.vue` |
| Feature directory | kebab-case | `user-profile/` |
| Composable | use + PascalCase | `useUserProfile.ts` |
| CSS Token | --kebab-case | `--brand-primary` |
| Emit event | kebab-case | `@update:model-value` |

## State files (.planning/ui/)

- Never delete — only overwrite or append
- Always include approval gate with checkboxes
- Include last update timestamp
- `project-ui-skill.md`: update with `/pwdev-uiux:scan` after structural changes

## Recommended commits per gate

```
Gate 1 approved: docs(ux): add spec for [feature]
Gate 3 completed: feat(ui): implement [ComponentName] in Vue
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
