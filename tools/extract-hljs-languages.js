// This script extracts the list of languages from highlight.js and outputs it.
//
// Example usage: node extract-languages.js FULL_PATH_TO_HIGHLIGHT_JS > languages.json
//
// Example output:
// {"name":"TypeScript","alias":"typescript"}
// {"name":"C++","alias":"cpp"}
const fs = require('fs');

const HIGHLIGHT_JS_PATH = process.argv[2]

const fileContent = fs.readFileSync(HIGHLIGHT_JS_PATH, 'utf8');
eval(fileContent);

let languages = hljs.listLanguages()

for (let languageAlias of languages) {
  let language = hljs.getLanguage(languageAlias)
  console.log(JSON.stringify({
    name: language.name,
    alias: languageAlias,
  }))
}
