/**
 * Idle Outpost daily giveaway claimer — Cloudflare Worker.
 *
 * Port of claim_api.py: logs into the Xsolla user-id service, lists the
 * "giveaway" virtual items, and claims any that still have availability.
 *
 * Runs on a cron trigger (see wrangler.jsonc) and also responds to GET /
 * for manual/debug invocation.
 */

const LOGIN_ENDPOINT = "https://sb-user-id-service.xsolla.com/api/v1/user-id";

export interface Env {
  IDLE_OUTPOST_USER_IDS: string;
  IDLE_OUTPOST_XSOLLA_PROJECT_ID: string;
  IDLE_OUTPOST_XSOLLA_MERCHANT_ID: string;
  IDLE_OUTPOST_XSOLLA_LOGIN_ID: string;
  IDLE_OUTPOST_XSOLLA_WEBHOOK_URL: string;
  IDLE_OUTPOST_SLACK_WEBHOOK?: string;
}

type ClaimStatus = "ok" | "skip" | "limit" | "error";

interface ClaimResult {
  name: string;
  sku: string;
  status: ClaimStatus;
  detail: string;
}

interface GiveawayItem {
  sku?: string;
  name?: string;
  limits?: {
    per_user?: {
      available?: number;
      recurrent_schedule?: { interval_type?: string };
    };
  };
}

function storeApiBase(env: Env): string {
  return `https://store.xsolla.com/api/v2/project/${env.IDLE_OUTPOST_XSOLLA_PROJECT_ID}`;
}

function userIds(env: Env): string[] {
  return (env.IDLE_OUTPOST_USER_IDS ?? "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

async function login(env: Env, userId: string): Promise<string> {
  const resp = await fetch(LOGIN_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      settings: {
        projectId: Number(env.IDLE_OUTPOST_XSOLLA_PROJECT_ID),
        merchantId: Number(env.IDLE_OUTPOST_XSOLLA_MERCHANT_ID),
      },
      loginId: env.IDLE_OUTPOST_XSOLLA_LOGIN_ID,
      webhookUrl: env.IDLE_OUTPOST_XSOLLA_WEBHOOK_URL,
      user: { id: userId, country: "KR" },
      isUserIdFromWebhook: false,
    }),
  });
  if (!resp.ok) {
    throw new Error(`login HTTP ${resp.status}: ${await resp.text()}`);
  }
  const data = (await resp.json()) as { token?: string };
  if (!data.token) {
    throw new Error("login response missing token");
  }
  return data.token;
}

async function getGiveawayItems(env: Env, token: string): Promise<GiveawayItem[]> {
  const url = new URL(`${storeApiBase(env)}/items/virtual_items/group`);
  url.searchParams.append("external_id[]", "giveaway");
  url.searchParams.set("locale", "en");
  url.searchParams.set("limit", "50");
  const resp = await fetch(url.toString(), {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!resp.ok) {
    throw new Error(`giveaway HTTP ${resp.status}: ${await resp.text()}`);
  }
  const data = (await resp.json()) as { items?: GiveawayItem[] };
  return data.items ?? [];
}

async function claimItem(env: Env, token: string, sku: string): Promise<number> {
  const resp = await fetch(`${storeApiBase(env)}/free/item/${sku}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  return resp.status;
}

async function claimAll(env: Env, userId: string): Promise<ClaimResult[]> {
  const results: ClaimResult[] = [];
  const token = await login(env, userId);
  const items = await getGiveawayItems(env, token);

  for (const item of items) {
    const sku = String(item.sku ?? "");
    const name = String(item.name ?? "");
    const perUser = item.limits?.per_user;
    const available = perUser?.available ?? 0;
    const interval = perUser?.recurrent_schedule?.interval_type ?? "?";

    if (typeof available !== "number" || available <= 0) {
      results.push({ name, sku, status: "skip", detail: `이미 수집됨 (${interval})` });
      continue;
    }

    const code = await claimItem(env, token, sku);
    if (code === 200 || code === 201 || code === 204) {
      results.push({ name, sku, status: "ok", detail: "수집 완료" });
    } else if (code === 422) {
      results.push({ name, sku, status: "limit", detail: "한도 도달" });
    } else {
      results.push({ name, sku, status: "error", detail: `HTTP ${code}` });
    }
  }
  return results;
}

function formatMessage(userResults: Record<string, ClaimResult[]>): string {
  const icons: Record<ClaimStatus, string> = {
    ok: "✅",
    skip: "⏭️",
    limit: "⏭️",
    error: "⚠️",
  };
  const sections: string[] = [];
  for (const [label, results] of Object.entries(userResults)) {
    const lines = results.map((r) => `${icons[r.status] ?? "•"} ${r.name} — ${r.detail}`);
    sections.push(`👤 ${label}\n${lines.join("\n")}`);
  }
  const ts = new Date().toLocaleString("sv-SE", { timeZone: "Asia/Seoul" });
  return `🎁 Idle Outpost 데일리 본어스\n\n${sections.join("\n\n")}\n\n📅 ${ts} KST`;
}

async function notifySlack(env: Env, message: string): Promise<void> {
  const webhook = (env.IDLE_OUTPOST_SLACK_WEBHOOK ?? "").trim();
  if (!webhook) return;
  try {
    await fetch(webhook, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: message }),
    });
  } catch (err) {
    console.warn("slack delivery failed", err);
  }
}

async function runClaim(env: Env): Promise<{ message: string; results: Record<string, ClaimResult[]> }> {
  const ids = userIds(env);
  if (ids.length === 0) {
    throw new Error("IDLE_OUTPOST_USER_IDS not set");
  }
  const userResults: Record<string, ClaimResult[]> = {};
  for (let i = 0; i < ids.length; i++) {
    const label = `Account ${i + 1}`;
    try {
      userResults[label] = await claimAll(env, ids[i]);
    } catch (err) {
      userResults[label] = [
        { name: "login", sku: "", status: "error", detail: String(err) },
      ];
    }
  }
  const message = formatMessage(userResults);
  await notifySlack(env, message);
  return { message, results: userResults };
}

export default {
  async scheduled(_controller: ScheduledController, env: Env, ctx: ExecutionContext): Promise<void> {
    ctx.waitUntil(
      runClaim(env).then(
        ({ message }) => console.log(message),
        (err) => console.error("scheduled claim failed", err),
      ),
    );
  },

  async fetch(_req: Request, env: Env): Promise<Response> {
    try {
      const out = await runClaim(env);
      return new Response(JSON.stringify(out, null, 2), {
        headers: { "Content-Type": "application/json; charset=utf-8" },
      });
    } catch (err) {
      return new Response(JSON.stringify({ error: String(err) }), {
        status: 500,
        headers: { "Content-Type": "application/json; charset=utf-8" },
      });
    }
  },
} satisfies ExportedHandler<Env>;
