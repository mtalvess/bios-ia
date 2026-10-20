// BIOS IA — aplicativo de computador do escritório.
// Janela com o escritório + "API" local (arquivo JSON) + Claude rodando no processo principal.
const { app, BrowserWindow, ipcMain, safeStorage, shell, Menu } = require("electron");
const path = require("path");
const fs = require("fs");
const crypto = require("crypto");
const Anthropic = require("@anthropic-ai/sdk").default;

const AGENTES = ["diretor", "conteudo", "designer", "video", "dev-sites", "comercial", "relatorios"];
const STATUS = ["afazer", "fazendo", "aprovar", "feito"];
const MODELO = "claude-opus-5-5";

// ---------- armazenamento local
const pasta = () => app.getPath("userData");
const arqDados = () => path.join(pasta(), "escritorio.json");
const arqChave = () => path.join(pasta(), "chave.bin");

function carregar() {
  try { return JSON.parse(fs.readFileSync(arqDados(), "utf8")); }
  catch {
    const seed = JSON.parse(fs.readFileSync(path.join(__dirname, "seed.json"), "utf8"));
    const d = { tarefas: seed.tarefas, atividade: seed.atividade };
    salvar(d);
    return d;
  }
}
function salvar(d) {
  fs.mkdirSync(pasta(), { recursive: true });
  const tmp = arqDados() + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify(d, null, 1));
  fs.renameSync(tmp, arqDados());
}
let dados;
const limpar = (s, n) => String(s ?? "").trim().slice(0, n);

function lerChave() {
  try {
    const buf = fs.readFileSync(arqChave());
    return safeStorage.isEncryptionAvailable() ? safeStorage.decryptString(buf) : buf.toString("utf8");
  } catch { return ""; }
}
function gravarChave(k) {
  fs.mkdirSync(pasta(), { recursive: true });
  const buf = safeStorage.isEncryptionAvailable() ? safeStorage.encryptString(k) : Buffer.from(k, "utf8");
  fs.writeFileSync(arqChave(), buf);
}

function criarTarefa(body) {
  const t = {
    id: crypto.randomUUID(),
    titulo: limpar(body.titulo, 80) || "Tarefa sem título",
    agente: AGENTES.includes(body.agente) ? body.agente : "diretor",
    detalhe: limpar(body.detalhe, 300),
    status: STATUS.includes(body.status) ? body.status : "afazer",
    ts: Date.now(),
  };
  dados.tarefas.unshift(t);
  salvar(dados);
  return t;
}
function registrar(agente, texto) {
  dados.atividade.unshift({ agente: AGENTES.includes(agente) ? agente : null, texto: limpar(texto, 300), ts: Date.now() });
  dados.atividade = dados.atividade.slice(0, 500);
  salvar(dados);
}

// ---------- Claude
const instr = (n) => { try { return fs.readFileSync(path.join(__dirname, "agentes", n), "utf8"); } catch { return ""; } };
const semCabecalho = (s) => s.replace(/^---[\s\S]*?---\s*/, "");
function cliente() {
  const k = lerChave();
  if (!k) throw Object.assign(new Error("sem chave"), { codigo: "sem_chave" });
  return new Anthropic({ apiKey: k });
}
async function pedir({ system, user, schema, effort = "medium", max_tokens = 8000 }) {
  const params = {
    model: MODELO,
    max_tokens,
    betas: ["server-side-fallback-2026-07-01"],
    fallbacks: "default",
    output_config: { effort, ...(schema ? { format: { type: "json_schema", schema } } : {}) },
    system,
    messages: [{ role: "user", content: user }],
  };
  const r = await cliente().beta.messages.create(params);
  if (r.stop_reason === "refusal") throw Object.assign(new Error("recusa"), { codigo: "recusa" });
  return r.content.filter((b) => b.type === "text").map((b) => b.text).join("");
}

const ESQUEMA_PLANO = {
  type: "object",
  properties: {
    resumo: { type: "string" },
    tarefas: {
      type: "array",
      items: {
        type: "object",
        properties: { titulo: { type: "string" }, agente: { type: "string", enum: AGENTES }, detalhe: { type: "string" } },
        required: ["titulo", "agente", "detalhe"],
        additionalProperties: false,
      },
    },
  },
  required: ["resumo", "tarefas"],
  additionalProperties: false,
};

async function diretor(texto) {
  registrar("diretor", `recebeu o pedido: "${limpar(texto, 120)}"`);
  const system =
    semCabecalho(instr("EMPRESA.md")) + "\n\n" + semCabecalho(instr("diretor.md")) +
    "\n\nAgora divida o pedido em 3 a 7 tarefas concretas, cada uma com título de até 60 caracteres, o id do agente responsável (diretor, conteudo, designer, video, dev-sites, comercial, relatorios) e o que entregar em uma frase. O resumo tem 1 a 2 frases.";
  const plano = JSON.parse(await pedir({ system, user: `Pedido do Mathias: ${texto}`, schema: ESQUEMA_PLANO, effort: "low", max_tokens: 4000 }));
  const tarefas = (plano.tarefas || []).slice(0, 7).map((k) => {
    const t = criarTarefa(k);
    registrar(k.agente, `recebeu: ${t.titulo}`);
    return t;
  });
  return { resumo: limpar(plano.resumo, 400), tarefas };
}

async function executar(id) {
  const t = dados.tarefas.find((x) => x.id === id);
  if (!t) throw Object.assign(new Error("não encontrada"), { codigo: "nao_encontrada" });
  t.status = "fazendo"; t.ts = Date.now(); salvar(dados);
  registrar(t.agente, `começou: ${t.titulo}`);
  const system =
    semCabecalho(instr("EMPRESA.md")) + "\n\n" + semCabecalho(instr(`${t.agente}.md`)) +
    "\n\nVocê está dentro do aplicativo BIOS IA e não tem acesso a arquivos nem à internet: entregue o trabalho em texto (Markdown), pronto para o Mathias revisar e aprovar. " +
    "Se a tarefa pede um arquivo visual ou vídeo, entregue o briefing completo (textos finais, cenas, cores, medidas) que a equipe usa para produzir. Onde faltar dado real, escreva [PREENCHER].";
  const user = `Tarefa: ${t.titulo}\nDetalhe: ${t.detalhe || "(sem detalhe)"}`;
  try {
    const texto = await pedir({ system, user, effort: "medium", max_tokens: 12000 });
    Object.assign(t, { resultado: texto, status: "aprovar", ts: Date.now() });
    salvar(dados);
    registrar(t.agente, `entregou para aprovação: ${t.titulo}`);
    return t;
  } catch (e) {
    t.status = "afazer"; t.ts = Date.now(); salvar(dados);
    registrar(t.agente, `não conseguiu concluir: ${t.titulo}`);
    throw e;
  }
}

// ---------- ponte com a página (mesmas rotas da versão web)
ipcMain.handle("bios:call", async (_e, { metodo, rota, corpo }) => {
  try {
    const [r, id] = rota.split("/");
    if (metodo === "GET" && r === "estado") return { ok: true, dados: { tarefas: dados.tarefas, atividade: dados.atividade.slice(0, 120) } };
    if (metodo === "POST" && r === "tarefas") return { ok: true, dados: criarTarefa(corpo || {}) };
    if (metodo === "PATCH" && r === "tarefas" && id) {
      const t = dados.tarefas.find((x) => x.id === id);
      if (!t) return { ok: false, erro: "Tarefa não encontrada." };
      if (corpo.status !== undefined && STATUS.includes(corpo.status)) t.status = corpo.status;
      if (corpo.titulo !== undefined) t.titulo = limpar(corpo.titulo, 80);
      if (corpo.detalhe !== undefined) t.detalhe = limpar(corpo.detalhe, 300);
      if (corpo.agente !== undefined && AGENTES.includes(corpo.agente)) t.agente = corpo.agente;
      t.ts = Date.now(); salvar(dados);
      return { ok: true, dados: t };
    }
    if (metodo === "POST" && r === "atividade") { registrar(corpo.agente, corpo.texto); return { ok: true, dados: {} }; }
    if (metodo === "POST" && r === "diretor") return { ok: true, dados: await diretor(limpar(corpo.texto, 2000)) };
    if (metodo === "POST" && r === "executar" && id) return { ok: true, dados: await executar(id) };
    return { ok: false, erro: "Rota não encontrada." };
  } catch (e) {
    if (e.codigo === "sem_chave") return { ok: false, codigo: "sem_chave", erro: "Configure sua chave do Claude primeiro." };
    if (e.codigo === "recusa") return { ok: false, erro: "O Claude recusou esse pedido. Reescreva de outro jeito." };
    if (e.status === 401) return { ok: false, codigo: "sem_chave", erro: "Chave do Claude inválida. Confira nas configurações." };
    if (e.status === 429) return { ok: false, erro: "Muitos pedidos seguidos. Tente de novo em alguns minutos." };
    if (e.status === 400 && /credit|billing/i.test(e.message || "")) return { ok: false, erro: "Sua conta da Anthropic está sem créditos." };
    return { ok: false, erro: "Falha ao falar com o Claude. Confira a internet e tente de novo." };
  }
});
ipcMain.handle("bios:temChave", () => !!lerChave());
ipcMain.handle("bios:salvarChave", (_e, k) => { gravarChave(String(k || "").trim()); return true; });
ipcMain.handle("bios:abrirPasta", () => shell.openPath(pasta()));

// ---------- janela
function criarJanela() {
  const w = new BrowserWindow({
    width: 1360, height: 900, minWidth: 420, minHeight: 600,
    backgroundColor: "#020A1C", title: "BIOS IA",
    icon: path.join(__dirname, "build", "icon.png"),
    webPreferences: { preload: path.join(__dirname, "preload.js"), contextIsolation: true, nodeIntegration: false, sandbox: true },
  });
  w.loadFile(path.join(__dirname, "app", "index.html"));
  w.webContents.setWindowOpenHandler(({ url }) => { if (/^https:\/\//.test(url)) shell.openExternal(url); return { action: "deny" }; });
  w.webContents.on("will-navigate", (e, url) => { if (!url.startsWith("file://")) { e.preventDefault(); if (/^https:\/\//.test(url)) shell.openExternal(url); } });
}

app.whenReady().then(() => {
  dados = carregar();
  Menu.setApplicationMenu(null);
  criarJanela();
  app.on("activate", () => { if (BrowserWindow.getAllWindows().length === 0) criarJanela(); });
});
app.on("window-all-closed", () => { if (process.platform !== "darwin") app.quit(); });
