# Anki Code Highlighter

An Anki plugin that adds syntax highlighting to code snippets.

<!-- markdownlint-disable-next-line -->
<p align="center"><img src="screenshots/animation-small.gif"/></p>

## Features

* Uses a color scheme that works in day and night modes.
* Works on Anki for desktop and AnkiDroid.

## Installation

### Fetching from AnkiWeb

You can install directly from
[AnkiWeb](https://ankiweb.net/shared/info/112228974) using Anki's add-on
management.

### Fetching from source

Alternatively you can install this plugin from source.

1. Run `package`.
2. Import `codehighlighter.ankiaddon` in Anki.

### Set up

After fetching, run `Extras > Configure Code Highlighter`. This is necessary
until Anki adds [add-on lifecycle
hooks](https://forums.ankiweb.net/t/install-update-delete-addon-hook-points/18532).

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

Run `testall` to run mypy and unit tests.

### Distribution

See [Anki's documentation on sharing
add-ons](https://addon-docs.ankiweb.net/#/sharing).

Use the `package` tool to create the zip.
