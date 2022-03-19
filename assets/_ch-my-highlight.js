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
  langs = ["c", "cpp", "go", "haskell", "java", "javascript", "python", "sql", "xml"];
  await Promise.allSettled(
    langs.map((lang) => loadScript("_ch-hljs-lang-" + lang + ".min.js")))
  hljs.highlightAll();
};
main();

