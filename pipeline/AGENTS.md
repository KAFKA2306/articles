# Pipeline engineering rules

Apply the root `AGENTS.md` first. For changes under `pipeline/`, also apply these rules.

## Complexity

Prefer the simplest self-contained change that fully satisfies the requirement and keeps the system working for users.

Decision order:

1. delete unnecessary code;
2. reuse the standard library, platform, framework, or existing repository capability;
3. compose existing abstractions;
4. add a dependency only when it removes more owned complexity than it creates;
5. write custom code only for behavior that remains uncovered.

For every implementation change, compare `before -> after`:

```text
user-visible capabilities  >=
verification / evidence    >=
owned LOC                  <=
files                      <=
direct dependencies        <=
manual steps               <=
```

An increase is allowed only when required for the requested outcome and explicitly justified by evidence. Do not game these measures through minification, generated/vendor code, hidden configuration, or by removing tests, types, observability, accessibility, or error reporting.

Prefer one small, independently verifiable change over speculative generalization or a larger framework.

Primary references:

- https://google.github.io/eng-practices/review/reviewer/looking-for.html
- https://google.github.io/eng-practices/review/developer/small-cls.html
