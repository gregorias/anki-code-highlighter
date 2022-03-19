# Anki Code Highlighter

WIP

An Anki plugin that add syntax highlighting to code snippets.

## Installation

1. Copy files in `assets` to your `collection.media` directory.
2. Append the following snippet to your cards:
  ```
  <link rel="stylesheet" href="_ch-my-solarized.css">
  <link rel="stylesheet" href="_ch-hljs-solarized.css">
  <script src='_ch-my-highlight.js'></script>
  ```
3. Package and install the addon.

## Design

* The only way to share files seems to be through `collection.media`.
* Anki does not support file directories in `collection.media`.

### Alternatives considered

#### Fetching CSS and JS assets from Internet

Loading files from Internet has the disadvantage of making my Anki solving
experience depend on Internet.

## For Developers

Use pipenv to set up the dev and prod environment.

### Testing

Run `testall` to run Mypy and unit tests.
