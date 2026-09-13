# Claude proxy inspector

A local HTTP proxy that forwards Claude Code traffic to `api.anthropic.com` and writes the last `/v1/messages` body to `out/request.json`. Everything under `out/` is gitignored.

## Start the proxy

```bash
node proxy.mjs
```

It listens on `127.0.0.1:8787` and overwrites `out/request.json` on every captured request.

## Send traffic through it

```bash
ANTHROPIC_BASE_URL=http://127.0.0.1:8787 claude -p "say ok" --model haiku
```

## Split the capture into markdown

System blocks joined into `out/SYSTEM.md`:

```bash
jq -r '[.system[]?.text] | join("\n\n---\n\n")' out/request.json > out/SYSTEM.md
```

One section per tool, with its schema, into `out/TOOLS.md`:

```bash
jq -r '[.tools[]? | "# \(.name)\n\n\(.description)\n\n```json\n\(.input_schema|tojson)\n```"] | join("\n\n---\n\n")' out/request.json > out/TOOLS.md
```

One section per message, text blocks only, into `out/MESSAGES.md`:

```bash
jq -r '[.messages[]? | "# \(.role)\n\n" + ([.content | if type=="string" then . else .[].text? // empty end] | join("\n\n"))] | join("\n\n---\n\n")' out/request.json > out/MESSAGES.md
```
