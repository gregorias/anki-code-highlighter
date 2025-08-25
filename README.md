# 🌈 Anki Code Highlighter

An Anki plugin that adds syntax highlighting to code snippets.

<!-- markdownlint-disable-next-line -->
<p align="center"><img src="screenshots/animation-small.gif"/></p>

## Features

* Uses a color scheme that works in day and night modes.
* Works on Anki for desktop and AnkiDroid.

## Installation

### Fetching from AnkiWeb

The recommended way to install this plugin is directly from
[AnkiWeb](https://ankiweb.net/shared/info/112228974) using Anki's add-on
management.

### Fetching from source

Alternatively, you can install this plugin from source.

1. Run `dev/bin/package`.
2. Import `codehighlighter.ankiaddon` in Anki.

## Usage

You can either highlight code from your clipboard or highlight a snippet of
code already present in a card field.

### Highlighting from clipboard

1. Put the cursor in the place you want to place your code.
2. Press `CTRL+'` (on macOS, `⌘+'`) or click this add-on's button in the
   editor's button bar.

### Highlighting an already written code snippet

1. Write a code snippet in a card editor.
2. Select the code snippet.
3. Press `CTRL+'` (on macOS, `⌘+'`) or click this add-on's button in the
   editor's button bar.

The plugin works on untagged code blocks. Do not add your own HTML tags like
`<code>` or `<pre><code>` to the snippet you want to highlight. If you have run
into issues with preannotated code snippets, see [this
comment](https://github.com/gregorias/anki-code-highlighter/issues/29#issuecomment-1367298126)
for how to fix this.

### Supported highlighters

This add-on uses [Pygments](https://pygments.org/).
It creates highlighting tags when you run this plugin.
This is useful for creating cloze cards.
It supports both inline code and code blocks.

### Configuration

The plugin accepts the following configuration options:

* `block-style` (default: "display:flex; justify-content:center;") — The CSS
  style applied to the outer most container of a block code snippet. The
  default centers the block.
* `css-files` (default lives in `codehighlighter/main.py`) — the list of CSS
  styles to use.
* `shortcut` (e.g. `ctrl+;`) — this sets the shortcut that triggers this
  plugin.

### Known limitations

#### Can't highlight split HTML nodes

If you see "The selection splits an HTML node, which prevents the highlighting
plugin from proceeding", you are partially selecting an HTML element.

This plugin can not highlight a selection that partially selects an HTML
element. To work around this, [see these
instructions](https://github.com/gregorias/anki-code-highlighter/issues/72#issuecomment-1830404297).

## Refresh & Removal

This plugin installs its own JS and CSS files. It also modifies card
templates. You need to run some manual steps if you:

* add a new template
* want to delete the plugin

If you add a new card template, run `Extras/Tools > Refresh Code Highlighter
Assets`.

To remove the plugin, run `Extras/Tools > Delete Code Highlighter Assets`
before deleting the plugin using Anki's internal add-on system. This
manual step is necessary until Anki adds [add-on lifecycle
hooks](https://forums.ankiweb.net/t/install-update-delete-addon-hook-points/18532).

## Custom Styles

This plugin supports a modified Solarized style out of the box (its day and
night variants) provided by two CSS stylesheets:

* `assets/_ch-hljs-solarized.css`
* `assets/_ch-pygments-solarized.css`

You may install your own style but defining and configuring custom stylesheets.

### Adding a custom style

To add a custom style, do the following:

1. Create your new CSS stylesheet. See subsections below for generation tips
   for each highlighter.
1. Rename the CSS stylesheet file to start with `_`. This is necessary to
   prevent garbage collection from Anki when you save it in the media
   directory. Let's say you named it `_ch-my-style.css`.
1. Save the CSS stylesheet file into [your Anki profile's media
   directory](https://docs.ankiweb.net/files.html). If you have already
   installed this plugin, the media directory should contain this plugin's
   assets, e.g., `_ch-hljs-solarized.css`.
1. Open this plugin's configuration in Anki and change the value of
   [`css-files`](#configuration) to use your new stylesheet, e.g.,:

   ```json
   {
     "css-files": [
       "_ch-my-style.css",
       "_ch-pygments-solarized.css",
     ]
   }
   ```

   In the example above, we keep the default styles for Pygments.
1. [Refresh this plugin's assets.](#refresh--removal)

### Generating a stylesheet for highlight.js

You may download a ready stylesheet for highlight.js from [the list of
available
styles](https://github.com/highlightjs/highlight.js/tree/main/src/styles).

You may customize it further by adding a custom border or adding a separate
style for dark mode. For how it's done, see
[`_ch-hljs-solarized.css`](https://github.com/gregorias/anki-code-highlighter/blob/main/assets/_ch-hljs-solarized.css).

### Generating a stylesheet for pygments

1. Modify `XXX_STYLE` variables in `dev/bin/generate-pygments-css` to use your
   desired style for each mode.
1. To generate a ready to use stylesheet, run `dev/bin/generate-pygments-css`.
   You may need to install a few dependencies for that script to run
   (`pygments`, `webcolors`). Import errors will guide you.
