# 🛠️ Developer documentation

This is a documentation file for Code Highlighter's developers.

## Dev environment setup

This section describes how to setup your development environment.

This project requires the following tools:

- [Commitlint]
- [Lefthook]
- [Just]
- [Markdownlint]
- [Poetry]
- [Pyenv]
- [Ruff]

1. Install the required Python version:

    ```shell
    pyenv install
    ```

1. Set up Poetry:

    ```shell
    poetry install
    ```

1. Install Lefthook:

    ```shell
    lefthook install
    ```

## Updating highlight.js

Anki code highlighter comes in bundled with the [highlight.js][hljs] JavaScript
package. The JS package's files are included in `assets`, e.g.,
`assets/_ch-highlight.js` contains the single-file implementation of
[highlight.js][hljs].

To update [highlight.js][hljs]:

1. Set `HLJS_VERSION` in `tools/hljs.py`.
1. Run `python tools/hljs.py`.

## Updating Pygments

Anki code hightlighter comes in bundled with the [Pygments] library, and its
version is tracked as a [Git
submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules) inside this
repository.

To update Pygments, go to the submodule and pull the desired version. For
example:

```shell
cd pydeps/pygments
git fetch
git checkout 2.18.0
```

## Generating Pygment stylesheets

In `assets/_ch-pygment-solarized.css` I keep the stylesheet for code formatted
with pygments plus a few lines for general styles. I generated the style there with
`dev/bin/pygutils.py` with some minor adjustments by hand:

1. There are some tech debt lines relevant for all `<pre><code>` tags.
2. I have added some custom styles for borders.

## Testing

1. Run unit tests and mypy with `just test`.
2. Test supported Anki versions (2.1.49 and latest) by packaging the plugin and
   importing the plugin into the lowest and the newest support Anki.

## Release & distribution

1. Create a release commit.
    1. Bump up the package version in `codehighlighter/manifest.json`
       and `pyproject.toml`.
    2. Tag the release commit `git tag vx.y.z && git push origin vx.y.z`.
1. Use the `dev/bin/package` tool to create `codehighlighter.ankiaddon`.
1. Create a GitHub release: `gh release create vx.y.z codehighlighter.ankiaddon`.
1. [Share the package on Anki.](https://addon-docs.ankiweb.net/#/sharing)

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

### Alternative methods of using highlight.js

I've added each highlight.js language as a separate script to assets/, and then
used another JS script to dynamically load languages. This method led to
visible lag in rendering as the number of languages grew, so I abandoned this.

I've then tried detecting which languages are used in the card. I had a bug,
where I did not properly account for language aliases. I've abandoned this way,
because I figured that it would way more fool-proof to just use a single
highlight.js bundle that has all languages. Loading that single file seems to
be fast.

## Updating Python

This package sets up a specific Python version to keep the dev environment in
sync with what Anki uses. To update this Python version, you need to:

1. If in the Poetry venv, deactivate it and remove it.
2. Update Python spec in `.python-version` and `pyproject.toml`.
3. Install the new Python version with `pyenv install`.
4. Install the new virtual environment with `poetry install`.

[Commitlint]: https://github.com/conventional-changelog/commitlint
[Lefthook]: https://github.com/evilmartians/lefthook
[Just]: https://github.com/casey/just
[Markdownlint]: https://github.com/igorshubovych/markdownlint-cli
[Poetry]: https://python-poetry.org
[Pyenv]: https://github.com/pyenv/pyenv
[Pygments]: https://github.com/pygments/pygments
[Ruff]: https://github.com/astral-sh/ruff
[hljs]: https://highlightjs.org/
