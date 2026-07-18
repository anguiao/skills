---
name: grilling
description: Stress-test and refine a draft spec through rigorous one-at-a-time questioning before implementation.
---

Read the draft spec first, then interview me relentlessly about every aspect of it until we reach a shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback on each question before continuing. Asking multiple questions at once is bewildering.

If a *fact* can be found by exploring the environment (filesystem, tools, etc.), look it up rather than asking me. The *decisions*, though, are mine — put each one to me and wait for my answer.

Keep the same spec updated and in `draft` as decisions are resolved; do not implement, commit, or invoke another workflow. After resolving all material decisions, make a final consistency pass and ask me to approve the spec. On approval, update its status using the repository's convention, defaulting to `approved`, then stop.
