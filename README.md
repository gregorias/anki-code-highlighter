# Anki Code Highlighter

An Anki plugin that adds syntax highlighting to code snippets.

<p align="center">
  <img src="screenshots/animation-small.gif"/>
</p>

## Features

* Uses a colorscheme that works on both in day and night modes.
* Works on Anki for desktop and AnkiDroid.


## Installation

1. Install the plugin using Anki's addon manager.
2. Run `Extras > Install Media Assets`.
3. Run `Extras > Set Up Cards`.

## Usage

1. Write a code snippet in a card editor.
2. Select your code snippet and press `CTRL+'`.

For the list of supported languages and their corresponding codes, see
`assets/_ch-hljs-lang-*.min.js` files.

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

### Distribution

See [Anki's documentation on sharing
add-ons](https://addon-docs.ankiweb.net/#/sharing).

Use the `package` tool to create the zip.
