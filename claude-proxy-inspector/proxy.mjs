import http from "node:http";
import https from "node:https";
import fs from "node:fs";
import path from "node:path";

const OUT = path.join(import.meta.dirname, "out");
const UP = "api.anthropic.com";

fs.mkdirSync(OUT, { recursive: true });

http
  .createServer((req, res) => {
    const chunks = [];
    req.on("data", (c) => chunks.push(c));
    req.on("end", () => {
      const body = Buffer.concat(chunks);
      if (req.url.includes("/v1/messages") && body.length) {
        const f = path.join(OUT, "request.json");
        fs.writeFileSync(f, body);
        console.error(`[captured] ${f} (${body.length} bytes)`);
      }
      const headers = { ...req.headers, host: UP };
      delete headers["content-length"];
      const up = https.request(
        { hostname: UP, port: 443, path: req.url, method: req.method, headers },
        (r) => {
          res.writeHead(r.statusCode, r.headers);
          r.pipe(res);
        },
      );
      up.on("error", (e) => {
        console.error("upstream err", e.message);
        res.writeHead(502);
        res.end();
      });
      if (body.length) up.write(body);
      up.end();
    });
  })
  .listen(8787, "127.0.0.1", () => console.error("proxy on 8787"));
