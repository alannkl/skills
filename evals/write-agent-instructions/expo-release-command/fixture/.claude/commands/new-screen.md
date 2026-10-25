---
description: Scaffold a new screen and register it in the navigator
argument-hint: <ScreenName>
---

Create a new screen called $ARGUMENTS.

1. Add `src/screens/$ARGUMENTSScreen.tsx` modeled on `src/screens/HomeScreen.tsx` (functional component, `StyleSheet.create` at the bottom).
2. Register it in `src/navigation/RootStack.tsx` and add its params to `RootStackParamList`.
3. Run `npx tsc --noEmit` and fix any type errors.
