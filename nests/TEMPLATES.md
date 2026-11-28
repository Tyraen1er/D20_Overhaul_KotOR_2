# Nest file templates

The nest guide gives the role of the six files; these templates set the exact form of
the two that Trieste reads in detail: `intent.md` and `choices.md`. Trieste reads this
form to display and edit them, and shows a file that strays too far from it only in the
simple view. `plan.md`, `documentation.md`, `handoff.md` and `inbox.md` are entirely
free.

## Common rules

- In the models below, each text between `<` and `>` describes what goes there; the
  rest is literal.
- A marker followed by `…`, such as `- …` or `### …`, means that the items or
  sections at that level may repeat.
- Plain Markdown, without HTML or HTML comments.
- A blank line separates headings, paragraphs and lists. A list item starts with
  `- ` at the beginning of the line, with no blank line after the previous item; its
  following lines and its sublists are indented by two spaces.

## intent.md

```markdown
# Definition

<Scope of the nest, in a single paragraph of at most 280 characters.>

## Lasting features

- [ ] <Lasting wish, stated as a verifiable fact.>
- [x] <Wish fulfilled and verified, which must remain true.>
- …

### <Optional subsection>

- [ ] <Lasting wish.>
- …

### …

## Working rules

- <Working rule, linking to its procedure if needed.>
- …

## One-off tasks

- <Remaining one-off task.>
- …
```

- The three sections are always present, even when empty.
- Each section may be split into `### <title>` subsections; items placed before the
  first one belong to none.
- Only the wishes of `## Lasting features` carry a checkbox: `[ ]` or `[x]`.

## choices.md

```markdown
## Open decisions

### <ID> — <Question put to the user>

<Free content: facts, options, consequences and suggestion.>

### …

## Projects on hold

### <Short name>

<Free content: the idea for later.>

### …
```

- `## Open decisions` opens the file and `## Projects on hold` ends it; both sections
  are always present, even when empty.
- Each decision is a `### <ID> — <question>` subsection; the identifier, unique within
  the nest, contains only letters, digits and hyphens (`D1`, `PDF-2`).
- Each project on hold is a `### <name>` subsection, without identifier.
- Inside a decision or a project, headings start at `####`.
