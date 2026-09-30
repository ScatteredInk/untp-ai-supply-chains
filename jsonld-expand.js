// Expand a credential with jsonld.js in safe mode, as the UNTP Playground does
// (tests-untp packages/untp-utils validate-jsonld.ts: safe: true). Contexts load
// from local copies; any other URL fails, like an unresolvable remote context.
//
// Usage: node jsonld-expand.js <credential.json>   -> prints {ok, expanded|error}

const fs = require("fs");
const path = require("path");
const jsonld = require("jsonld");

const LOCAL = {
  "https://www.w3.org/ns/credentials/v2": "schemas/contexts/credentials-v2.jsonld",
  "https://vocabulary.uncefact.org/untp/0.7.0/context/": "schemas/contexts/untp-0.7.0-context.jsonld",
  "https://example.org/untp-ai/0.1/context.jsonld": "extension/untp-ai-context.jsonld",
};

async function documentLoader(url) {
  const file = LOCAL[url];
  if (!file) throw new Error(`context-fetch: no local copy for ${url}`);
  return {
    contextUrl: null,
    documentUrl: url,
    document: JSON.parse(fs.readFileSync(path.join(__dirname, file), "utf8")),
  };
}

(async () => {
  const doc = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
  try {
    const expanded = await jsonld.expand(doc, { documentLoader, safe: true });
    console.log(JSON.stringify({ ok: true, expanded }));
  } catch (e) {
    console.log(JSON.stringify({ ok: false, error: `${e.name}: ${e.message}`, details: e.details || null }));
  }
})();
