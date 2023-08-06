// This script extracts the list of languages from highlight.js and outputs it.
//
// Example usage: node extract-languages.js FULL_PATH_TO_HIGHLIGHT_JS > languages.json
//
// Example output:
// {"name":"TypeScript","alias":"typescript"}
// {"name":"C++","alias":"cpp"}

const HIGHLIGHT_JS_PATH = process.argv[2]

// If HIGHLIGHT_JS_PATH is not a relative path, this require might fail,
// because the relative path needs to be with respect to the script's
// location.
hljs = require(HIGHLIGHT_JS_PATH)
let languages = hljs.listLanguages()

for (let languageAlias of languages) {
  let language = hljs.getLanguage(languageAlias)
  console.log(JSON.stringify({
    name: language.name,
    alias: languageAlias,
  }))
}
