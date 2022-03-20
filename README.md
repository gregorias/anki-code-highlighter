# Anki Code Highlighter

WIP

An Anki plugin that add syntax highlighting to code snippets.

## Installation

1. Append the following snippet to your cards:
  ```
  <link rel="stylesheet" href="_ch-my-solarized.css">
  <link rel="stylesheet" href="_ch-hljs-solarized.css">
  <script src='_ch-my-highlight.js'></script>
  ```
2. Package and install the addon.
3. Delete old media files and install the new ones using the menu.
4. Copy the assets to AnkiDroid's collection.media (the sync doesn't seem to work).

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
