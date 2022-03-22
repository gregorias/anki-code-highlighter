async function loadScript(url) {
  return new Promise((resolve, reject) => {
    // Adding the script tag to the head as suggested before
    let head = document.head;
    let script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = url;
    script.async = false;

    script.onload = resolve;
    script.onerror = reject;

    document.head.appendChild(script);
  })
};

async function main() {
  await loadScript("_ch-highlight.js");
  langs = [
    "armasm",
    "avrasm",
    "c",
    "clojure",
    "coq",
    "cpp",
    "csharp",
    "go",
    "groovy",
    "haskell",
    "java",
    "javascript",
    "kotlin",
    "php",
    "python",
    "r",
    "ruby",
    "rust",
    "sql",
    "swift",
    "typescript",
    "vbnet",
    "vim",
    "wasm",
    "xml"];
  await Promise.allSettled(
    langs.map((lang) => loadScript("_ch-hljs-lang-" + lang + ".min.js")))
  hljs.highlightAll();
};
main();

