// API do Escritório BIOS IA (Cloudflare Pages Functions + D1).
// Rotas (todas exigem o cabeçalho x-senha igual à variável SENHA):
//   GET   /api/estado            → { tarefas, atividade }
//   POST  /api/tarefas           → cria tarefa { titulo, agente, detalhe?, status? }
//   PATCH /api/tarefas/:id       → altera campos da tarefa
//   POST  /api/atividade         → registra { agente, texto }
//   POST  /api/diretor           → { texto } — o Diretor (Claude) divide o pedido em tarefas
import Anthropic from "@anthropic-ai/sdk";
import seed from "../../seed.json";

const AGENTES = ["diretor", "conteudo", "designer", "video", "dev-sites", "comercial", "relatorios"];
const STATUS = ["afazer", "fazendo", "aprovar", "feito"];

const json = (data, status = 200) =>
  new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

async function preparar(db) {
  await db.batch([
    db.prepare("CREATE TABLE IF NOT EXISTS tarefas (id TEXT PRIMARY KEY, data TEXT NOT NULL, ts INTEGER NOT NULL)"),
    db.prepare("CREATE TABLE IF NOT EXISTS atividade (id TEXT PRIMARY KEY, data TEXT NOT NULL, ts INTEGER NOT NULL)"),
    db.prepare("CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT)"),
  ]);
  const ok = await db.prepare("SELECT v FROM meta WHERE k = 'seed'").first();
  if (ok) return;
  const stmts = [];
  for (const { id, ...t } of seed.tarefas) stmts.push(db.prepare("INSERT OR IGNORE INTO tarefas (id, data, ts) VALUES (?, ?, ?)").bind(id, JSON.stringify(t), t.ts));
  for (const { id, ...a } of seed.atividade) stmts.push(db.prepare("INSERT OR IGNORE INTO atividade (id, data, ts) VALUES (?, ?, ?)").bind(id, JSON.stringify(a), a.ts));
  stmts.push(db.prepare("INSERT OR REPLACE INTO meta (k, v) VALUES ('seed', '1')"));
  await db.batch(stmts);
}

const limpar = (s, n) => String(s ?? "").trim().slice(0, n);

async function criarTarefa(db, body) {
  const agente = AGENTES.includes(body.agente) ? body.agente : "diretor";
  const t = {
    titulo: limpar(body.titulo, 80) || "Tarefa sem título",
    agente,
    detalhe: limpar(body.detalhe, 300),
    status: STATUS.includes(body.status) ? body.status : "afazer",
    ts: Date.now(),
  };
  if (body.pedido) t.pedido = limpar(body.pedido, 60);
  const id = crypto.randomUUID();
  await db.prepare("INSERT INTO tarefas (id, data, ts) VALUES (?, ?, ?)").bind(id, JSON.stringify(t), t.ts).run();
  return { id, ...t };
}

async function registrar(db, agente, texto) {
  const a = { agente: AGENTES.includes(agente) ? agente : null, texto: limpar(texto, 300), ts: Date.now() };
  await db.prepare("INSERT INTO atividade (id, data, ts) VALUES (?, ?, ?)").bind(crypto.randomUUID(), JSON.stringify(a), a.ts).run();
}

const ESQUEMA = {
  type: "object",
  properties: {
    resumo: { type: "string" },
    tarefas: {
      type: "array",
      items: {
        type: "object",
        properties: {
          titulo: { type: "string" },
          agente: { type: "string", enum: AGENTES },
          detalhe: { type: "string" },
        },
        required: ["titulo", "agente", "detalhe"],
        additionalProperties: false,
      },
    },
  },
  required: ["resumo", "tarefas"],
  additionalProperties: false,
};

async function diretor(env, db, texto) {
  const client = new Anthropic({ apiKey: env.ANTHROPIC_API_KEY });
  const response = await client.beta.messages.create({
    model: "claude-opus-5-5",
    max_tokens: 4000,
    betas: ["server-side-fallback-2026-07-01"],
    fallbacks: "default",
    output_config: { effort: "low", format: { type: "json_schema", schema: ESQUEMA } },
    system:
      "Você é o Diretor da BIOS, empresa de Campina Grande-PB que faz sites, cardápios digitais, apps de agendamento, sistemas de gestão e automação de atendimento para pequenos negócios (Instagram @b1os.fc). " +
      "Regras: nada é publicado ou enviado sem aprovação do dono (Mathias); não invente números, clientes ou depoimentos; não use personagens ou marcas de terceiros em peças comerciais. " +
      "Equipe: diretor (planejamento), conteudo (ganchos, roteiros, legendas), designer (posts, carrosséis), video (reels, filmes, convites), dev-sites (sites, cardápios digitais), comercial (propostas, atendimento), relatorios (números). " +
      "Divida o pedido em 3 a 7 tarefas concretas, cada uma com título de até 60 caracteres, o id do agente responsável e o que entregar em uma frase. O resumo tem 1 a 2 frases.",
    messages: [{ role: "user", content: `Pedido do Mathias: ${texto}` }],
  });
  if (response.stop_reason === "refusal") throw Object.assign(new Error("refusal"), { code: "refusal" });
  const texto_json = response.content.filter((b) => b.type === "text").map((b) => b.text).join("");
  const plano = JSON.parse(texto_json);
  const tarefas = [];
  for (const k of (plano.tarefas || []).slice(0, 7)) {
    tarefas.push(await criarTarefa(db, { titulo: k.titulo, agente: k.agente, detalhe: k.detalhe }));
    await registrar(db, k.agente, `recebeu: ${limpar(k.titulo, 80)}`);
  }
  return { resumo: limpar(plano.resumo, 400), tarefas };
}

export async function onRequest({ request, env, params }) {
  if (!env.DB) return json({ erro: "Banco D1 não configurado (binding DB)." }, 500);
  if (!env.SENHA) return json({ erro: "Defina a variável SENHA no projeto." }, 500);
  if (request.headers.get("x-senha") !== env.SENHA) return json({ erro: "Senha incorreta." }, 401);

  const db = env.DB;
  await preparar(db);
  const partes = params.path || [];
  const rota = partes[0];
  const metodo = request.method;
  const corpo = metodo === "GET" ? {} : await request.json().catch(() => ({}));

  try {
    if (metodo === "GET" && rota === "estado") {
      const t = await db.prepare("SELECT id, data FROM tarefas ORDER BY ts DESC").all();
      const a = await db.prepare("SELECT data FROM atividade ORDER BY ts DESC LIMIT 120").all();
      return json({
        tarefas: t.results.map((r) => ({ id: r.id, ...JSON.parse(r.data) })),
        atividade: a.results.map((r) => JSON.parse(r.data)),
      });
    }
    if (metodo === "POST" && rota === "tarefas") return json(await criarTarefa(db, corpo), 201);
    if (metodo === "PATCH" && rota === "tarefas" && partes[1]) {
      const linha = await db.prepare("SELECT data FROM tarefas WHERE id = ?").bind(partes[1]).first();
      if (!linha) return json({ erro: "Tarefa não encontrada." }, 404);
      const t = JSON.parse(linha.data);
      if (corpo.status !== undefined) { if (!STATUS.includes(corpo.status)) return json({ erro: "Status inválido." }, 400); t.status = corpo.status; }
      if (corpo.titulo !== undefined) t.titulo = limpar(corpo.titulo, 80);
      if (corpo.detalhe !== undefined) t.detalhe = limpar(corpo.detalhe, 300);
      if (corpo.agente !== undefined && AGENTES.includes(corpo.agente)) t.agente = corpo.agente;
      t.ts = Date.now();
      await db.prepare("UPDATE tarefas SET data = ?, ts = ? WHERE id = ?").bind(JSON.stringify(t), t.ts, partes[1]).run();
      return json({ id: partes[1], ...t });
    }
    if (metodo === "POST" && rota === "atividade") { await registrar(db, corpo.agente, corpo.texto); return json({ ok: true }, 201); }
    if (metodo === "POST" && rota === "diretor") {
      if (!env.ANTHROPIC_API_KEY) return json({ erro: "Defina o segredo ANTHROPIC_API_KEY para o Diretor trabalhar." }, 500);
      const texto = limpar(corpo.texto, 2000);
      if (!texto) return json({ erro: "Escreva o pedido." }, 400);
      await registrar(db, "diretor", `recebeu o pedido: "${limpar(texto, 120)}"`);
      return json(await diretor(env, db, texto));
    }
    return json({ erro: "Rota não encontrada." }, 404);
  } catch (e) {
    if (e?.code === "refusal") return json({ erro: "O Diretor recusou esse pedido. Reescreva de outro jeito." }, 422);
    if (e?.status === 429) return json({ erro: "Muitos pedidos seguidos. Tente de novo em alguns minutos." }, 429);
    return json({ erro: "Falha ao processar. Tente de novo." }, 500);
  }
}
