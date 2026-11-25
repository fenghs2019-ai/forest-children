/**
 * 森林诗网智能体对话服务
 * - 静态托管对话页（白名单路径）
 * - POST /api/chat：代理腾讯云混元 ChatCompletions（流式 SSE 转发）
 * - 密钥只存在于服务端（private/config.json），静态白名单不会放行
 * 用法：node server.js（监听 PORT 环境变量，默认 3000）
 */
const http = require("http");
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const PORT = parseInt(process.env.PORT || "3000", 10);
const ROOT = __dirname;

/* ── 密钥配置 ── */
let CFG = null;
try {
  CFG = JSON.parse(fs.readFileSync(path.join(ROOT, "private", "config.json"), "utf-8"));
} catch (e) {
  console.error("[warn] private/config.json 不存在，/api/chat 将返回未配置提示");
}

/* ── 混元客户端 ── */
let hunyuan = null;
const MODEL_DEFAULT = (CFG && CFG.model) || "hunyuan-lite";
function getHunyuan() {
  if (!CFG) return null;
  if (!hunyuan) {
    const tencentcloud = require("tencentcloud-sdk-nodejs-hunyuan");
    const HunyuanClient = tencentcloud.hunyuan.v20230901.Client;
    hunyuan = new HunyuanClient({
      credential: { secretId: CFG.secretId, secretKey: CFG.secretKey },
      region: CFG.region || "ap-beijing",
      profile: { httpProfile: { endpoint: "hunyuan.tencentcloudapi.com" } }
    });
  }
  return hunyuan;
}

/* ── 简单限流：每 IP 每小时 40 次 ── */
const RATE = { max: 40, windowMs: 3600 * 1000 };
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
// 定期清理
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
  if (p === "/" || p === "") p = "index.html";
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

/* ── /api/chat 代理 ── */
function handleChat(req, res, body) {
  if (!CFG) {
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
  // 大小护栏：总字符数 ≤ 240000（语料约 6 万字，留余量）
  const total = msgs.reduce((n, m) => n + (typeof m.content === "string" ? m.content.length : 0), 0);
  if (total > 240000) {
    res.writeHead(413, { "Content-Type": "application/json; charset=utf-8" });
    return res.end(JSON.stringify({ error: { code: "request_too_large", message: "对话过长" } }));
  }
  // 只允许 user/assistant/system 角色，content 必须是字符串；混元 API 要求 Role/Content 大写字段
  const clean = msgs.map(m => ({ Role: String(m.role), Content: String(m.content) }))
    .filter(m => ["user", "assistant", "system"].includes(m.Role));
  if (!clean.length) {
    res.writeHead(400, { "Content-Type": "application/json; charset=utf-8" });
    return res.end(JSON.stringify({ error: { code: "request_invalid_parameter", message: "messages 参数无效" } }));
  }

  const client = getHunyuan();
  const model = typeof parsed.model === "string" && /^[\w.\-]{1,64}$/.test(parsed.model)
    ? parsed.model : MODEL_DEFAULT;

  res.writeHead(200, {
    "Content-Type": "text/event-stream; charset=utf-8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no"
  });
  const send = (event, data) => res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);

  const onClose = () => { try { req.destroy(); } catch (e) {} };
  res.on("close", onClose);

  const params = {
    Model: model,
    Messages: clean,
    Stream: true,
    Temperature: 0.9
  };
  client.ChatCompletions(params).then(stream => {
    stream.on("data", data => {
      const d = data && data.Choice && data.Choice.Delta && data.Choice.Delta.Content;
      if (d) send("delta", { content: d });
      if (data && data.Choice && data.Choice.FinishReason) send("done", { finishReason: data.Choice.FinishReason });
    });
    stream.on("end", () => { send("done", {}); res.end(); });
    stream.on("error", err => {
      console.error("[hunyuan stream]", err && err.message);
      send("error", { code: "model_error", message: "模型服务暂时不可用" });
      res.end();
    });
  }).catch(err => {
    const code = (err && err.code) || "internal_error";
    console.error("[hunyuan call]", code, err && err.message);
    send("error", { code: code === "AuthFailure.SignatureFailure" || String(code).startsWith("AuthFailure")
      ? "auth_failed" : "model_error", message: "森林的门暂时打不开，请稍后再试" });
    res.end();
  });
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
  console.log(`forest-children-agents listening on :${PORT}, model=${MODEL_DEFAULT}, keys=${CFG ? "loaded" : "MISSING"}`);
});
