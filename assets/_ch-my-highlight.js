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

/**
 * @param {HighlightedHTMLElement} block - the HTML element to determine language for
 */
function codeBlockLanguage(block) {
  let classes = block.className;
  let languageClass = classes
    .split(/\s+/)
    .find((_class) => _class.startsWith("language-"));
  if (!languageClass) return null;
  return languageClass.replace("language-", "");
}

function removeDuplicates(array) {
  return [...new Set(array)];
}

function removeNulls(array) {
  return array.filter((item) => item);
}

function findUsedLanguages() {
  let codeBlocks = document.querySelectorAll("pre code");
  if (!codeBlocks) return [];
  let languageArray = Array.from(codeBlocks).map(codeBlockLanguage);
  languageArray = removeNulls(languageArray);
  return removeDuplicates(languageArray);
}

async function main() {
  // If we are called too early in the loading process, defer until later.
  // We can't find the active code blocks until the page is fully loaded.
  if (document.readyState === "loading") {
    window.wantsHighlight = true;
    return;
  }

  // Only load the languages that are actually used on the page.
  // Loading all available languages is too slow and leads to visible
  // flickering even on M1 Macs.
  let usedLanguages = findUsedLanguages();

  // Don't load anything if there are no code blocks.
  if (usedLanguages.length === 0) return;

  await loadScript("_ch-highlight.js");
  await Promise.allSettled(
    usedLanguages.map((lang) => loadScript("_ch-hljs-lang-" + lang + ".min.js")))
  hljs.highlightAll();
};

function boot() {
  if (window.wantsHighlight) main();
}

main();
if (typeof window !== 'undefined' && window.addEventListener) {
  window.addEventListener('DOMContentLoaded', boot, false);
}
