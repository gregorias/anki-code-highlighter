async function loadScript(url) {
  return new Promise((resolve, reject) => {
    // Adding the script tag to the head as suggested before
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
    "bash",
    "c",
    "clojure",
    "coq",
    "cpp",
    "csharp",
    "css",
    "go",
    "groovy",
    "haskell",
    "java",
    "javascript",
    "kotlin",
    "latex",
    "lisp",
    "lua",
    "php",
    "plaintext",
    "protobuf",
    "python",
    "python-repl",
    "r",
    "ruby",
    "rust",
    "scss",
    "shell",
    "sql",
    "swift",
    "typescript",
    "vbnet",
    "vim",
    "wasm",
    "yaml",
    "xml"];
  await Promise.allSettled(
    langs.map((lang) => loadScript("_ch-hljs-lang-" + lang + ".min.js")))
  hljs.highlightAll();
};
main();

