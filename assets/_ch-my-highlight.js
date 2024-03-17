// Only highlight code blocks with the class `language-*`.
// `language-*` is a classes added by this plugin’s markup.
// See https://github.com/gregorias/anki-code-highlighter/issues/76.
hljs.configure({
  cssSelector: 'pre code[class^="language-"]',
});
hljs.highlightAll();
