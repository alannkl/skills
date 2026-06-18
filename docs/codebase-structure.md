# Codebase Structure Principles

Good codebase structure optimizes for change. It makes it obvious where things belong, what depends on what, and how to change behavior without surprising the rest of the system. These principles are means to that end, not goals by themselves.

The point is not architectural purity. The point is to keep code cheap to understand, safe to change, and honest about what the system is.

## 1. Structure Around Change

The best structure makes the next correct change the easiest one to make.

It is not the structure that looks most orderly. It is the one that lowers the cost of the change you have not made yet. Group things that change together. Separate things that change for different reasons, at different rates, or under different ownership.

Design check: when a cluster changes often, ask what interface callers should depend on so future changes stay local. A useful module concentrates behavior behind a small surface; a pass-through module just moves the same complexity somewhere else.

## 2. Organize by Domain, Not by Technical Role

The top level should reveal what the system does, not what it is built with.

Group by capability: billing, auth, search, onboarding, reporting. Avoid making the primary structure a set of technical buckets like controllers, models, views, services, or helpers, which scatter one feature across the tree.

Technical roles still matter inside a domain. They should not be how the system explains itself. Most other structure follows from this choice because features usually change as features.

## 3. Maximize Cohesion, Minimize Coupling

Each unit does one thing whose parts need each other, and touches other units as little as practical.

Each file, module, package, feature area, or subsystem should do one conceptual thing whose parts genuinely belong together. Different units should connect through narrow, intentional surfaces.

Good structure maximizes the work you can do while looking at one place, and minimizes how far a change ripples outward.

Design check: prefer deep modules. A deep module gives callers a lot of useful behavior through a small interface. A shallow module exposes almost as much complexity as it hides, so callers still need to understand too much.

## 4. Make Boundaries Explicit

Every unit exposes a deliberate public surface and keeps the rest internal.

A good structure shows where one part ends and another begins. Other code should depend on the public surface, not on implementation details. That surface is the contract: it lets internals change without forcing every caller to change too.

The goal is not more layers. The goal is understandable ownership.

Design check: treat an interface as everything a caller must know to use the unit correctly: parameters, invariants, ordering constraints, error modes, configuration, and performance expectations. The type signature is only part of the interface.

## 5. Put Replacement Points Where Behavior Actually Varies

A replacement point is useful when it lets behavior change without editing the caller.

A boundary says where ownership changes. A replacement point says where behavior can be swapped. They are related, but not identical.

Use replacement points for real variation: external systems, volatile infrastructure, alternate implementations, test doubles for true boundaries, or places where policy and mechanism need to vary independently. Do not introduce a new replacement point just because one might be useful someday.

Design check: one adapter usually means hypothetical variation; two adapters means the variation is real. If only one implementation exists and no current force needs replacement, keep the structure simpler.

## 6. Point Dependencies Toward Stability

Dependencies should flow toward what changes least.

Domain rules, policies, workflows, and invariants should be more stable than frameworks, APIs, databases, UI, infrastructure, and vendor SDKs. Let volatile edges depend on the stable center, not the reverse.

This prevents circular dependencies and hidden coupling, and it protects core logic from churn. Cycles are a serious smell because they fuse separate parts into one inseparable whole.

Design check: adapters belong near volatility. A database repository, vendor client, HTTP handler, queue worker, or UI adapter can satisfy a stable interface, but the stable center should not know the details of that adapter.

## 7. Split by Reason-to-Change, Not by Size

Divide on reasons to change, never on line count.

Divide a unit when it carries multiple reasons to change, serves multiple audiences, mixes levels of abstraction, or combines stable policy with volatile details.

Do not split code just because it crossed a line-count threshold. Size is a weak smell, not a reason in itself: treat unusual size as a prompt to look for hidden reasons-to-change, and split on those if you find them. Reason-to-change is the real signal. A long but cohesive file is often healthier than several fragments you must hold open at once to understand one flow.

Design check: before splitting, ask whether the new unit will have a real interface with leverage. If the split only creates forwarding functions, extra names, and more navigation, it has probably made the structure shallower. The new unit can be a directory of cohesive modules — promoting `routes.ts` to `routes/` with one module per domain is sound when each module is a real boundary, but not when the pieces are arbitrary slices or the folder exists only to re-export them.

## 8. Keep Related Things Close

Distance in the tree should track conceptual distance.

Files that are usually read, changed, tested, or reviewed together should live near each other. If understanding one behavior means jumping across many unrelated folders, the structure makes the reader pay interest on every change.

Design check: keep tests near the behavior they verify, and test through the same interface callers use. If a test must reach past the interface to prove normal behavior, the interface or module shape may be wrong.

## 9. Avoid Junk Drawers

Shared code earns a specific name and a clear reason to exist.

Folders named `common`, `shared`, `utils`, `helpers`, or `misc` drift into unowned dumping grounds where cohesion disappears. Give shared code a specific name and a clear reason: `validation`, `http-client`, `auth-token`, `permissions`, `logging`.

Promote something to shared when there is a second real consumer, not a guessed future one. If something is shared, it should be more carefully designed, not less. If a thing has no clear name, it may not yet have a clear responsibility.

Design check: use the deletion test. If deleting the shared module makes complexity vanish, it was probably a pass-through. If deleting it causes the same logic to reappear across many callers, it was earning its place.

## 10. Make the Easy Path the Right Path

Good structure guides good decisions without constant discipline.

Adding a feature, test, endpoint, command, screen, or integration should naturally land in the correct place, use the correct public surface, and avoid forbidden dependencies. If doing the right thing feels like swimming upstream, the structure is not carrying enough weight.

Design check: the intended interface should be easier to use than reaching into internals. If callers routinely bypass the public surface, either the surface is too weak or the structure is hiding the wrong thing.

## 11. Optimize for the Reader

Code is read more than written, and navigated more than read.

Names should make intent obvious. Locations should be predictable. A newcomer should be able to guess where something belongs and often be right.

The structure is documentation. Make it tell the truth.

Design check: use precise names for structural roles. A module has an interface and an implementation. An adapter is a concrete implementation at a replacement point. Prefer the clearest domain name over a generic structural name.

## 12. Match Structure to Scale

Use the simplest structure that protects the code from its current failure modes.

Small systems want simple structure. Large systems need stronger boundaries. Stay flat and simple until complexity demands hierarchy, then add it where the pain is, not in anticipation.

Premature architecture creates friction. Delayed architecture creates entropy. Promote something to shared, layered, abstracted, or replaceable when a real second case appears, not a guessed future one.

Design check: deep modules are valuable at any scale, but formal boundaries and adapters should scale with actual variation. In a small codebase, a plain function can be the right module. In a larger one, the same concept may deserve a package, interface, and adapters.

## 13. Enforce the Load-Bearing Rules

Write down what matters; enforce the rules whose violation makes change unsafe.

Structure should not rely on tribal knowledge. Write down the boundaries, naming conventions, dependency rules, ownership expectations, and module responsibilities that matter.

Documentation is the floor, not the ceiling. A rule everyone ignores is just tidier tribal knowledge. Enforce the load-bearing rules with something automatic where practical: package visibility, lint rules, import restrictions, dependency checks, CI, ownership files, or review gates.

Do not enforce everything. Enforce the rules whose violation would make the system harder to change safely.

Design check: enforcement should protect real interfaces and dependency direction. It should not freeze private implementation details or make local refactoring expensive.

## Balancing the Forces

These are forces to balance, not boxes to maximize. Cohesion, simplicity, explicit boundaries, useful interfaces, flexibility, and enforcement sometimes pull against each other. Strict boundaries at small scale become over-engineering; minimal structure at large scale becomes entropy.

In one sentence: structure code around ownership, change patterns, and dependency boundaries; keep related things close; keep unrelated things separate; point dependencies toward stable logic; and make the obvious place to put new work also the correct place. Use module-design concepts only when they make those structural choices clearer, safer, and easier to test.
