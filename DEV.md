# 🛠️ Developer documentation

This is a documentation file for Code Highlighter's developers.

## Dev Environment Setup

This section describes how to setup your development environment.

This project requires the following tools:

- [Commitlint]
- [Lefthook]
- [Markdownlint]

1. Install the required Python version:

    ```shell
    pyenv install CHECK_PIPFILE
    ```

1. Set up Pipenv:

    ```shell
    pipenv install --dev
    ```

1. Install Lefthook:

    ```shell
    lefthook install
    ```

## Updating highlight.js

`_assets/_cs-highlight.js` contains the single-file implementation of
[highlight.js][hljs]. It comes from the ZIP package available on [their main
site][hljs].

## Generating Pygment stylesheets

In `assets/_ch-pygment-solarized.css` I keep the stylesheet for code formatted
with pygments plus a few lines for general styles. I generated the style there with
`dev/bin/pygutils.py` with some minor adjustments by hand:

1. There are some tech debt lines relevant for all `<pre><code>` tags.
2. I have added some custom styles for borders.

## Testing

1. Run unit tests and mypy with `testall`.
2. Test supported Anki versions (2.1.49 and latest) by packaging the plugin and
   importing the plugin into the lowest and the newest support Anki.

## Release & distribution

1. Create a release commit.
    1. Bump up the package version in `codehighlighter/manifest.json`.
    2. Tag the release commit `git tag vx.y.z && git push origin vx.y.z`.
2. Use the `dev/bin/package` tool to create `codehighlighter.ankiaddon`.
3. [Share the package on Anki.](https://addon-docs.ankiweb.net/#/sharing)

## Design Decisions

This section discuss some design decisions made for this plugin.

### Highlighter concept

One fundamental abstraction is that of **highlighter**. A highlighter is
essentially a function that produces an HTML representing a highlighted code
snippet given the following:

- A string with the unmarked code snippet.
- A language that code snippet represents.
- Additional styling options.

For code clarity and modularity, I keep such pure highlighters in separate
modules (`hljs` and `pygments`). A highlighter does not implement any logic
related to Anki including sanitising input from HTML markup.

### Using `assets/_ch*` files for CSS and JS

The asset files start with an underscore, because then Anki ignores them
([source](https://anki.tenderapp.com/discussions/ankidesktop/39510-anki-is-completely-ignoring-media-files-starting-with-underscores-when-cleaning-up)).

This plugin saves its assets directly in the global `assets` directory.

- The only way to share files across desktop and mobile seems to be through
  `collection.media`.
- Anki does not support file directories in `collection.media`.

#### Alternatives considered

##### Fetching CSS and JS assets from Internet

Loading files from Internet has the disadvantage of making my Anki solving
experience depend on Internet, which I don't think is reasonable on mobile.

### Card template instrumentation mode

The plugin instruments all card templates by default, because that's what most
people will want. It requires zero-effort from a user to get to what they want,
which is being able to highlight code. It's non-intrusive, the added styles
should not interfere with users' preexisting settings as they are namespaced by
a class (`hljs` or `pygments`).

[Commitlint]: https://github.com/conventional-changelog/commitlint
[Lefthook]: https://github.com/evilmartians/lefthook
[Markdownlint]: https://github.com/igorshubovych/markdownlint-cli
[hljs]: https://highlightjs.org/
