/**
 * 森林诗网智能体对话服务
 * - 静态托管对话页（白名单路径）
 * - POST /api/chat：代理腾讯云 TokenHub（OpenAI 兼容协议，混元 Hy3 等模型），流式 SSE 转发
 *   · TokenHub 不可用时自动降级到旧混元 SDK（若配置了 secretId/secretKey）
 * - 密钥只存在于服务端（private/config.json），静态白名单不会放行
 * 用法：node server.js（监听 PORT 环境变量，默认 3000）
 */
const http = require("http");
const https = require("https");
const fs = require("fs");
const path = require("path");

const PORT = parseInt(process.env.PORT || "3000", 10);
const ROOT = __dirname;

/* ── 密钥配置 ── */
let CFG = null;
try {
  CFG = JSON.parse(fs.readFileSync(path.join(ROOT, "private", "config.json"), "utf-8"));
} catch (e) {
  console.error("[warn] private/config.json 不存在，/api/chat 将返回未配置提示");
}

const TH = (CFG && CFG.tokenhub) || null;
const TH_READY = !!(TH && TH.apiKey);
const MODEL_DEFAULT = (TH && TH.model) || (CFG && CFG.model) || "hy3-preview";
const MODEL_FALLBACKS = (TH && Array.isArray(TH.fallbacks)) ? TH.fallbacks : [];

/* ── 旧混元 SDK（兜底） ── */
let legacy = null;
function getLegacy() {
  if (!CFG || !CFG.secretId) return null;
  if (!legacy) {
    const tencentcloud = require("tencentcloud-sdk-nodejs-hunyuan");
    const C = tencentcloud.hunyuan.v20230901.Client;
    legacy = new C({
      credential: { secretId: CFG.secretId, secretKey: CFG.secretKey },
      region: CFG.region || "ap-beijing",
      profile: { httpProfile: { endpoint: "hunyuan.tencentcloudapi.com" } }
    });
  }
  return legacy;
}

/* ── 简单限流：每 IP 每小时 60 次 ── */
const RATE = { max: 60, windowMs: 3600 * 1000 };
const hits = new Map();
function rateLimited(ip) {
  const now = Date.now();
  const rec = hits.get(ip);
  if (!rec || now > rec.resetAt) {
    hits.set(ip, { count: 1, resetAt: now + RATE.windowMs });
    return false;
  }
  rec.count += 1;
  return rec.count > RATE.max;
}
setInterval(() => {
  const now = Date.now();
  for (const [k, v] of hits) if (now > v.resetAt) hits.delete(k);
}, 600000).unref();

/* ── 静态白名单 ── */
const STATIC_FILES = new Set([
  "index.html", "list.html", "new.html",
  "agent.html", "chat.html", "agent-data.js",
  "forest.css", "favicon.ico", "favicon-32.png", "apple-touch-icon.png", "icon-192.png"
]);
const STATIC_DIRS = ["fonts/", "sdk/", "audio/"];
const MIME = {
  ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8", ".json": "application/json; charset=utf-8",
  ".woff2": "font/woff2", ".woff": "font/woff", ".ttf": "font/ttf",
  ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif",
  ".svg": "image/svg+xml", ".ico": "image/x-icon", ".mp3": "audio/mpeg", ".txt": "text/plain; charset=utf-8"
};
function serveStatic(req, res, urlPath) {
  let p = urlPath.split("?")[0];
  if (p === "/" || p === "") p = "agent.html";
  p = decodeURIComponent(p).replace(/\\/g, "/");
  const file = path.normalize(path.join(ROOT, p));
  if (!file.startsWith(ROOT)) { res.writeHead(403); return res.end(); }
  const rel = path.relative(ROOT, file).replace(/\\/g, "/");
  const allowed =
    STATIC_FILES.has(rel) ||
    STATIC_DIRS.some(d => rel.startsWith(d) && !rel.slice(d.length).includes("/.."));
  if (!allowed) { res.writeHead(404); return res.end("Not Found"); }
  fs.readFile(file, (err, data) => {
    if (err) { res.writeHead(404); return res.end("Not Found"); }
    res.writeHead(200, {
      "Content-Type": MIME[path.extname(file).toLowerCase()] || "application/octet-stream",
      "Cache-Control": rel.endsWith(".html") || rel === "agent-data.js" || rel === "forest.css"
        ? "no-cache, must-revalidate"
        : "public, max-age=604800"
    });
    res.end(data);
  });
}

/* ── TokenHub（OpenAI 兼容）流式调用 ── */
function callTokenHub(model, roles, send) {
  return new Promise((resolve, reject) => {
    const payload = JSON.stringify({
      model: model,
      messages: roles,
      stream: true,
      temperature: 0.9
    });
    const base = String(TH.baseUrl || "https://tokenhub.tencentmaas.com/v1").replace(/\/+$/, "");
    const u = new URL(base + "/chat/completions");
    const rq = https.request({
      hostname: u.hostname,
      path: u.pathname + (u.search || ""),
      method: "POST",
      headers: {
        "Authorization": "Bearer " + TH.apiKey,
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(payload),
        "Accept": "text/event-stream"
      }
    }, r => {
      if (r.statusCode !== 200) {
        let b = "";
        r.setEncoding("utf-8");
        r.on("data", c => { b += c; });
        r.on("end", () => {
          let code = "upstream_" + r.statusCode, msg = b.slice(0, 300);
          try {
            const j = JSON.parse(b);
            const e = j.error || (j.Response && j.Response.Error);
            if (e) { code = e.code || e.type || code; msg = e.message || msg; }
          } catch (e) {}
          reject(Object.assign(new Error(msg), { code }));
        });
        return;
      }
      let buf = "";
      r.setEncoding("utf-8");
      r.on("data", chunk => {
        buf += chunk;
        let i;
        while ((i = buf.indexOf("\n\n")) >= 0) {
          const raw = buf.slice(0, i); buf = buf.slice(i + 2);
          for (const line of raw.split("\n")) {
            if (!line.startsWith("data:")) continue;
            const data = line.slice(5).trim();
            if (!data || data === "[DONE]") continue;
            try {
              const j = JSON.parse(data);
              const ch0 = j.choices && j.choices[0];
              const d = ch0 && ch0.delta;
              if (d && d.content) send("delta", { content: d.content });
              if (ch0 && ch0.finish_reason) send("done", { finishReason: ch0.finish_reason });
            } catch (e) {}
          }
        }
      });
      r.on("end", () => resolve());
      r.on("error", reject);
    });
    rq.on("error", reject);
    rq.setTimeout(120000, () => rq.destroy(new Error("upstream_timeout")));
    rq.write(payload);
    rq.end();
  });
}

/* ── 旧混元 SDK 流式调用（兜底） ── */
function callLegacyHunyuan(model, clean, send) {
  return new Promise((resolve, reject) => {
    const client = getLegacy();
    if (!client) return reject(Object.assign(new Error("legacy not configured"), { code: "not_configured" }));
    client.ChatCompletions({ Model: model, Messages: clean, Stream: true, Temperature: 0.9 })
      .then(stream => {
        stream.on("data", data => {
          const d = data && data.Choice && data.Choice.Delta && data.Choice.Delta.Content;
          if (d) send("delta", { content: d });
        });
        stream.on("end", () => resolve());
        stream.on("error", reject);
      })
      .catch(reject);
  });
}

/* ── /api/chat 代理 ── */
function handleChat(req, res, body) {
  if (!CFG || (!TH_READY && !CFG.secretId)) {
    res.writeHead(503, { "Content-Type": "application/json; charset=utf-8" });
    return res.end(JSON.stringify({ error: { code: "not_configured", message: "服务密钥未配置" } }));
  }
  let parsed;
  try { parsed = JSON.parse(body); } catch (e) {
    res.writeHead(400, { "Content-Type": "application/json; charset=utf-8" });
    return res.end(JSON.stringify({ error: { code: "request_invalid_parameter", message: "请求体不是合法 JSON" } }));
  }
  const msgs = Array.isArray(parsed.messages) ? parsed.messages : null;
  if (!msgs || !msgs.length || msgs.length > 40) {
    res.writeHead(400, { "Content-Type": "application/json; charset=utf-8" });
    return res.end(JSON.stringify({ error: { code: "request_invalid_parameter", message: "messages 参数无效" } }));
  }
  const total = msgs.reduce((n, m) => n + (typeof m.content === "string" ? m.content.length : 0), 0);
  if (total > 240000) {
    res.writeHead(413, { "Content-Type": "application/json; charset=utf-8" });
    return res.end(JSON.stringify({ error: { code: "request_too_large", message: "对话过长" } }));
  }
  // OpenAI 风格 role/content
  const roles = msgs
    .map(m => ({ role: String(m.role), content: String(m.content) }))
    .filter(m => ["user", "assistant", "system"].includes(m.role));
  // 旧混元要求 Role/Content 大写
  const clean = roles.map(m => ({ Role: m.role, Content: m.content }));
  if (!roles.length) {
    res.writeHead(400, { "Content-Type": "application/json; charset=utf-8" });
    return res.end(JSON.stringify({ error: { code: "request_invalid_parameter", message: "messages 参数无效" } }));
  }

  res.writeHead(200, {
    "Content-Type": "text/event-stream; charset=utf-8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no"
  });
  const send = (event, data) => { try { res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`); } catch (e) {} };
  res.on("close", () => { try { req.destroy(); } catch (e) {} });

  // 模型链：配置默认 + 服务端降级
  const chain = [MODEL_DEFAULT, ...MODEL_FALLBACKS].filter((m, i, a) => m && a.indexOf(m) === i);

  (async () => {
    let lastErr = null;
    for (let i = 0; i < chain.length; i++) {
      const model = chain[i];
      try {
        if (TH_READY) await callTokenHub(model, roles, send);
        else await callLegacyHunyuan(model, clean, send);
        send("done", {});
        return res.end();
      } catch (e) {
        lastErr = e;
        const code = String((e && e.code) || "");
        const msg = String((e && e.message) || "");
        const retryable = /model|invalid|param|not_?found|unsupported|404|400/i.test(code + " " + msg);
        console.error("[chat]", model, code, msg.slice(0, 160));
        if (i < chain.length - 1 && retryable) continue;
        break;
      }
    }
    const code = String((lastErr && lastErr.code) || "model_error");
    const friendly = /auth|unauthor|401|403/i.test(code)
      ? "森林的门暂时打不开，管理员正在处理，请稍后再试"
      : "森林的门暂时打不开，请稍后再试";
    send("error", { code: code, message: friendly });
    res.end();
  })();
}

/* ── HTTP 服务 ── */
const server = http.createServer((req, res) => {
  const urlPath = req.url || "/";
  if (req.method === "POST" && urlPath.split("?")[0] === "/api/chat") {
    const ip = (req.headers["x-forwarded-for"] || req.socket.remoteAddress || "?").split(",")[0].trim();
    if (rateLimited(ip)) {
      res.writeHead(429, { "Content-Type": "application/json; charset=utf-8" });
      return res.end(JSON.stringify({ error: { code: "quota_rate_limited", message: "森林今天太热闹了，稍后再来吧" } }));
    }
    let body = "", over = false;
    req.on("data", c => {
      body += c;
      if (body.length > 1400000) { over = true; req.destroy(); }
    });
    req.on("end", () => { if (!over) handleChat(req, res, body); });
    return;
  }
  if (req.method === "GET" || req.method === "HEAD") return serveStatic(req, res, urlPath);
  res.writeHead(405); res.end();
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`forest-children-agents listening :${PORT} | tokenhub=${TH_READY ? "on(" + MODEL_DEFAULT + ")" : "off"} | legacy=${CFG && CFG.secretId ? "on" : "off"}`);
});
