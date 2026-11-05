/* ON COURT ONLY storefront | vanilla JS single-page app, no build step. */
(() => {
  "use strict";
  const $ = (s, el = document) => el.querySelector(s);
  const app = $("#app");
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const money = (n) => (n == null ? "–" : "A$" + Number(n).toLocaleString("en-AU", { minimumFractionDigits: 0, maximumFractionDigits: 2 }));
  const state = { me: null, departments: [] };

  // ------------------------------------------------------------ API
  async function api(path, opts = {}) {
    const init = { credentials: "same-origin", headers: {} };
    if (opts.method && opts.method !== "GET") {
      init.method = opts.method;
      init.headers["X-Requested-With"] = "oco";
      init.headers["Content-Type"] = "application/json";
      init.body = JSON.stringify(opts.body || {});
    }
    const res = await fetch("/api" + path, init);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw Object.assign(new Error(data.error || res.statusText), { status: res.status });
    return data;
  }

  // ------------------------------------------------------------ era
  function setEra(era, persist = true) {
    document.documentElement.dataset.era = era;
    document.querySelectorAll("[data-era-btn]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.eraBtn === era)));
    if (persist) try { localStorage.setItem("oco-era", era); } catch (e) { /* storage unavailable */ }
    const route = location.hash.split("?")[0];
    if (route === "#/" || route === "" || route === "#") render();
  }
  document.querySelectorAll("[data-era-btn]").forEach((b) => b.addEventListener("click", () => { setEra(b.dataset.eraBtn); snapSound(1); }));
  try { const saved = localStorage.getItem("oco-era"); if (saved) setEra(saved, false); } catch (e) { /* ignore */ }
  const era = () => document.documentElement.dataset.era;

  $("#menu-toggle").addEventListener("click", (e) => {
    const nav = $("#nav"); nav.classList.toggle("open");
    e.currentTarget.setAttribute("aria-expanded", nav.classList.contains("open"));
  });

  // ------------------------------------------------------------ sound: original synthesised snap
  let actx;
  function snapSound(count = 5) {
    try {
      actx = actx || new (window.AudioContext || window.webkitAudioContext)();
      for (let i = 0; i < count; i++) {
        const t = actx.currentTime + i * 0.055 + Math.random() * 0.012;
        const len = 0.035;
        const buf = actx.createBuffer(1, Math.floor(actx.sampleRate * len), actx.sampleRate);
        const d = buf.getChannelData(0);
        for (let j = 0; j < d.length; j++) d[j] = (Math.random() * 2 - 1) * Math.pow(1 - j / d.length, 3);
        const src = actx.createBufferSource(); src.buffer = buf;
        const bp = actx.createBiquadFilter(); bp.type = "bandpass"; bp.frequency.value = 2400 + Math.random() * 900; bp.Q.value = 1.4;
        const g = actx.createGain(); g.gain.value = 0.55;
        src.connect(bp).connect(g).connect(actx.destination); src.start(t);
      }
    } catch (e) { /* audio unavailable */ }
  }

  // ------------------------------------------------------------ original garment illustrations
  function art(spec = {}, size = 260) {
    const c1 = spec.c1 || "#333", c2 = spec.c2 || "#999", c3 = spec.c3 || "#fff";
    const pin = spec.pin ? `<pattern id="pin${c1.slice(1)}" width="9" height="9" patternUnits="userSpaceOnUse"><rect width="9" height="9" fill="${c1}"/><rect x="4" width="1.2" height="9" fill="${c3}" opacity=".55"/></pattern>` : "";
    const fill = spec.pin ? `url(#pin${c1.slice(1)})` : c1;
    const snaps = (x, y0, n, gap, cls = "") => Array.from({ length: n }, (_, i) => `<circle class="snapdot ${cls}" cx="${x}" cy="${y0 + i * gap}" r="3.4" fill="${c3}" stroke="#000" stroke-opacity=".35"/>`).join("");
    const shapes = {
      pants: `<g><rect x="70" y="24" width="120" height="16" rx="3" fill="${c2}"/>
        <g class="leg-left"><path d="M70 40 64 60l10 200h42l14-160V40z" fill="${fill}" stroke="#000" stroke-opacity=".25" stroke-width="2"/>
          <path d="M70 40 64 60l10 200h10l-6-200z" fill="${c2}"/>${snaps(72, 66, 11, 18)}</g>
        <g class="leg-right"><path d="M130 40h60l6 20-10 200h-42l-14-160z" fill="${fill}" stroke="#000" stroke-opacity=".25" stroke-width="2"/>
          <path d="M190 40l6 20-10 200h-10l6-200z" fill="${c2}"/>${snaps(188, 66, 11, 18, "r")}</g></g>`,
      jacket: `<g><path d="M86 34l44 12 44-12 46 26-14 70-22-8v130H76V122l-22 8-14-70z" fill="${fill}" stroke="#000" stroke-opacity=".25" stroke-width="2"/>
        <path d="M108 38l22 30 22-30" fill="none" stroke="${c2}" stroke-width="8"/><rect x="128" y="64" width="4" height="190" fill="${c3}" opacity=".85"/>
        <path d="M40 60l14 70 22-8" fill="none" stroke="${c2}" stroke-width="10"/><path d="M220 60l-14 70-22-8" fill="none" stroke="${c2}" stroke-width="10"/>
        <rect x="76" y="238" width="108" height="14" fill="${c2}"/></g>`,
      shirt: `<g><path d="M92 34h76l52 28-16 50-24-10v150H80V102l-24 10-16-50z" fill="${fill}" stroke="#000" stroke-opacity=".25" stroke-width="2"/>
        <path d="M108 34q22 22 44 0" fill="none" stroke="${c2}" stroke-width="7"/><path d="M40 62l16 50" stroke="${c2}" stroke-width="9"/><path d="M220 62l-16 50" stroke="${c2}" stroke-width="9"/>
        <rect x="80" y="140" width="100" height="10" fill="${c2}" opacity=".9"/></g>`,
      jersey: `<g><path d="M96 30h18q16 26 32 0h18l18 40q10 6 18 0l-6 190H66l-6-190q8 6 18 0z" fill="${fill}" stroke="#000" stroke-opacity=".25" stroke-width="2"/>
        <path d="M114 30q16 26 32 0" fill="none" stroke="${c2}" stroke-width="7"/><text x="130" y="170" text-anchor="middle" font-family="Bowlby One SC, Impact, sans-serif" font-size="66" fill="${c2}" stroke="${c3}" stroke-width="2">00</text></g>`,
      shoe: `<g transform="translate(0 40)"><path d="M30 150q0-40 36-54l40-48q22-12 40 6l14 28q34 6 64 28 26 20 6 40z" fill="${c1}" stroke="#000" stroke-opacity=".3" stroke-width="2"/>
        <path d="M24 150h214q6 0 4 14l-4 10H30q-10 0-8-12z" fill="${c3}"/><path d="M60 118q50-8 120 6" fill="none" stroke="${c2}" stroke-width="10" stroke-linecap="round"/>
        <circle cx="120" cy="70" r="6" fill="${c2}"/><circle cx="134" cy="82" r="6" fill="${c2}"/></g>`,
    };
    return `<svg viewBox="0 0 260 280" width="${size}" role="img" aria-label="Original illustration (not a photo of the item)"><defs>${pin}</defs>${shapes[spec.g] || shapes.shirt}</svg>`;
  }

  const badge = (cls, label) => `<span class="badge b-${esc(cls)}">${esc(label || cls.replace(/_/g, " "))}</span>`;
  function card(p) {
    const skin = p.era === "OG" ? "skin-og" : "skin-current";
    return `<a class="card ${skin}" href="#/item/${esc(p.slug)}">
      <div class="art">${p.season ? `<span class="season-tag">${esc(p.season)}</span>` : ""}${art(p.art, 200)}</div>
      <div class="meta"><div>${badge(p.classification, p.classification_label)} ${p.is_demo ? badge("demo", "Demo") : ""}</div>
        <h3>${esc(p.title)}</h3><div class="muted" style="font-size:.85rem">${esc(p.team_or_school || "")}</div>
        <div class="row"><span class="price">${p.price_aud ? money(p.price_aud) : ""}</span><span class="mono muted">${esc(p.availability)}</span></div></div></a>`;
  }

  // ------------------------------------------------------------ router
  const routes = {
    "": home, "shop": shop, "item": item, "teams": teams, "team": team, "aussies": aussies, "player": player,
    "vault": vault, "exchange": exchange, "locker": locker, "standards": standards, "account": account, "admin": admin,
  };
  function parse() {
    const h = location.hash.replace(/^#\/?/, "");
    const [path, qs] = h.split("?");
    const parts = path.split("/").filter(Boolean);
    return { name: parts[0] || "", arg: parts[1], q: new URLSearchParams(qs || "") };
  }
  async function render() {
    const r = parse();
    document.querySelectorAll("nav.main a").forEach((a) => a.classList.toggle("on", a.dataset.nav === r.name));
    $("#nav").classList.remove("open");
    const fn = routes[r.name] || home;
    try { await fn(r); } catch (e) { app.innerHTML = `<div class="wrap loading">${esc(e.message)}</div>`; }
    window.scrollTo(0, 0);
  }
  window.addEventListener("hashchange", render);

  // ------------------------------------------------------------ pages
  async function home() {
    const og = era() === "og";
    const [products, depts, players] = await Promise.all([api("/products?limit=12"), api("/departments"), api("/players")]);
    state.departments = depts;
    const featured = products.filter((p) => (og ? p.era === "OG" : p.era === "CURRENT")).slice(0, 4);
    const current = players.filter((p) => p.status === "CURRENT_NBA");
    const heroSpec = og ? { g: "pants", c1: "#5b2a86", c2: "#00838f", c3: "#f1e6cc", pin: true } : { g: "pants", c1: "#2a3442", c2: "#c1ed57", c3: "#f8f5eb" };
    app.innerHTML = `
    <section class="hero"><div class="wrap hero-grid">
      <div>
        <div class="mono kicker">${og ? "ON COURT OG · 1996 onward" : "CURRENT COURT · the modern game"}</div>
        <h1 class="display">${og ? "Remember<em>the sound?</em>" : "Wear the game.<em>Not just the logo.</em>"}</h1>
        <p class="lede">${og
          ? "The snap of warmups coming off before tip-off. We find the genuine team-issued gear from those seasons, prove where it came from, and bring it to Australian collectors."
          : "Team-issued equipment from today's NBA and NCAA, sourced through legitimate releases and documented piece by piece. Gear you saw on court. Gear you couldn't get."}</p>
        <div class="ctas"><a class="btn accent" href="#/vault">Enter the Tearaway Vault</a><a class="btn alt" href="#/shop?era=${og ? "OG" : "CURRENT"}">Browse ${og ? "OG" : "Current"} exhibits</a></div>
        <div class="snaprow" aria-hidden="true">${"<span></span>".repeat(9)}</div>
      </div>
      <div class="hero-art"><div class="stamp">${og ? "Team issue · verified" : "Provenance on file"}</div>
        <button class="icon-btn snap-stage" id="hero-snap" aria-label="Play the tearaway snap">${art(heroSpec, 340)}</button>
        <div class="mono muted" style="text-align:center">Tap the pants · original illustration</div></div>
    </div></section>

    <section class="block"><div class="wrap">
      <div class="section-head"><h2 class="display">The departments</h2><span class="mono muted">${products.length} demo exhibits · 0 items for sale</span></div>
      <div class="depts">${depts.map((d) => `<a class="dept" href="#/shop?department=${d.code}"><span class="mono muted count">${d.count}</span><h3>${esc(d.name)}</h3><p>${esc(d.blurb)}</p></a>`).join("")}
        <a class="dept" href="#/locker"><h3>The Locker Room</h3><p>Community, collector stories and the wanted board.</p></a></div>
    </div></section>

    <section class="block" style="border-top:var(--card-border)"><div class="wrap">
      <div class="section-head"><h2 class="display">${og ? "From the archive" : "Current court exhibits"}</h2><a class="btn alt" href="#/shop">All exhibits</a></div>
      <div class="grid">${featured.map(card).join("")}</div>
    </div></section>

    <section class="block" style="border-top:var(--card-border)"><div class="wrap">
      <div class="section-head"><h2 class="display">Australians on court</h2><a class="btn alt" href="#/aussies">Full register</a></div>
      <p class="muted">${current.length} Australians named on 2026-27 NBA rosters in our register, each with a cited source. Every connection on this site is sourced; if we can't source it, we don't say it.</p>
      <div class="chips">${current.map((p) => `<a class="chip" href="#/player/${esc(p.id)}">${esc(p.name)} · ${esc((p.stints || "").split(";")[0])}</a>`).join("")}</div>
    </div></section>

    <section class="block" style="border-top:var(--card-border)"><div class="wrap">
      <div class="section-head"><h2 class="display">Authentic on court = verified team issue</h2><a class="btn alt" href="#/standards">Our standards</a></div>
      <div class="era-strip">
        ${[["Team-Issued", "Made or supplied for team use, proven by official provenance, an authenticator, or custody plus construction evidence."],
           ["Player-Issued", "Allocated to a named player. Allocated is not the same as worn, and we never blur the two."],
           ["Player-Worn Premium", "Only with a wear letter or an independent photo-match to a specific event."],
           ["Licensed Retail", "Genuine fan merchandise, kept in the Logo Archive and always labelled as retail."]]
          .map(([h, t]) => `<div class="panel"><div class="mono muted">Class</div><h3 class="display" style="font-size:1.4rem;margin:6px 0">${h}</h3><p style="margin:0">${t}</p></div>`).join("")}
      </div>
    </div></section>

    <section class="block" style="border-top:var(--card-border)"><div class="wrap" style="max-width:760px">
      <h2 class="display" style="font-size:clamp(2rem,5vw,3rem)">Get the first drop</h2>
      <p>Join the launch list for first access to the first 30 verified pieces. We only email when there's something real to show you.</p>
      ${waitlistForm("home")}
    </div></section>`;
    $("#hero-snap").addEventListener("click", (e) => { snapSound(7); e.currentTarget.classList.toggle("torn"); });
    bindWaitlist();
  }

  function waitlistForm(source) {
    return `<form class="form" id="waitlist" data-source="${source}">
      <div class="two"><label>Email<input type="email" name="email" required autocomplete="email"></label>
        <label>Era<select name="era"><option value="OG">ON COURT OG</option><option value="CURRENT">Current Court</option><option value="BOTH">Both</option></select></label></div>
      <label>Teams or schools you collect (optional)<input name="teams" maxlength="200" placeholder="e.g. Bulls, Saint Mary's"></label>
      <label class="check"><input type="checkbox" name="consent" required> I agree to receive ON COURT ONLY launch and drop emails. I can unsubscribe at any time.</label>
      <button class="btn accent" type="submit">Join the list</button><div class="out"></div></form>`;
  }
  function bindWaitlist() {
    const f = $("#waitlist"); if (!f) return;
    f.addEventListener("submit", async (e) => {
      e.preventDefault(); const fd = new FormData(f);
      try {
        const r = await api("/waitlist", { method: "POST", body: { email: fd.get("email"), era: fd.get("era"), teams: fd.get("teams"), consent: !!fd.get("consent"), source: f.dataset.source } });
        $(".out", f).innerHTML = `<div class="msg ok">${esc(r.message)}</div>`; f.reset();
      } catch (err) { $(".out", f).innerHTML = `<div class="msg err">${esc(err.message)}</div>`; }
    });
  }

  async function shop(r) {
    const q = r.q;
    const depts = state.departments.length ? state.departments : await api("/departments");
    state.departments = depts;
    const dept = depts.find((d) => d.code === q.get("department"));
    const params = new URLSearchParams();
    ["q", "department", "era", "league", "item_type", "classification", "sort"].forEach((k) => q.get(k) && params.set(k, q.get(k)));
    const items = await api("/products?" + params);
    const opt = (name, vals, label) => `<select name="${name}" aria-label="${label}"><option value="">${label}</option>${vals.map(([v, l]) => `<option value="${v}" ${q.get(name) === v ? "selected" : ""}>${l}</option>`).join("")}</select>`;
    app.innerHTML = `<section class="block"><div class="wrap">
      <div class="section-head"><div><div class="mono muted">${dept ? "Department" : "All exhibits"}</div><h2 class="display">${esc(dept ? dept.name : "Shop the archive")}</h2>
        ${dept ? `<p class="muted" style="margin:6px 0 0">${esc(dept.blurb)}</p>` : ""}</div><span class="mono muted">${items.length} results</span></div>
      <div class="chips"><a class="chip ${!dept ? "on" : ""}" href="#/shop">All</a>${depts.map((d) => `<a class="chip ${dept && dept.code === d.code ? "on" : ""}" href="#/shop?department=${d.code}">${esc(d.name)}</a>`).join("")}</div>
      <form class="toolbar" id="filters">
        <input type="search" name="q" placeholder="Search team, season, item…" value="${esc(q.get("q") || "")}" aria-label="Search">
        ${opt("era", [["OG", "ON COURT OG"], ["CURRENT", "Current Court"]], "Any era")}
        ${opt("league", [["NBA", "NBA"], ["NCAA", "NCAA"]], "Any league")}
        ${opt("item_type", [["TEARAWAY_PANTS", "Tearaway pants"], ["WARMUP_JACKET", "Warmup jackets"], ["SHOOTING_SHIRT", "Shooting shirts"], ["JERSEY", "Jerseys"], ["PRACTICE", "Practice gear"], ["SHOES", "Shoes"]], "Any item")}
        ${opt("classification", [["TEAM_ISSUED", "Team-Issued"], ["VINTAGE_TEAM_ISSUE", "Vintage Team Issue"], ["PLAYER_ISSUED", "Player-Issued"], ["PLAYER_WORN", "Player-Worn"], ["RARE_KICKS", "Rare Kicks"], ["LICENSED_RETAIL", "Licensed Retail"]], "Any class")}
        ${opt("sort", [["season", "Season"], ["price_asc", "Price low-high"], ["price_desc", "Price high-low"]], "Featured")}
        ${dept ? `<input type="hidden" name="department" value="${esc(dept.code)}">` : ""}
        <button class="btn" type="submit">Filter</button></form>
      <div class="grid">${items.map(card).join("") || `<p class="muted">Nothing here yet. <a href="#/locker">Post a wanted item</a> and we'll hunt for it.</p>`}</div>
    </div></section>`;
    $("#filters").addEventListener("submit", (e) => {
      e.preventDefault(); const fd = new FormData(e.target); const p = new URLSearchParams();
      for (const [k, v] of fd.entries()) if (v) p.set(k, v);
      location.hash = "#/shop?" + p;
    });
    $("#filters").addEventListener("change", (e) => { if (e.target.tagName === "SELECT") e.currentTarget.requestSubmit(); });
  }

  async function item(r) {
    const p = await api("/products/" + encodeURIComponent(r.arg));
    const a = p.authentication;
    const ref = p.media.find((m) => m.side === "REFERENCE");
    const skin = p.era === "OG" ? "skin-og" : "skin-current";
    const evidence = p.evidence.map((e) => `<li><b>${esc(e.code.replace(/_/g, " "))}</b>${e.reference_id ? ` <span class="mono muted">${esc(e.reference_id)}</span>` : ""}${e.detail ? ` · ${esc(e.detail)}` : ""}</li>`).join("");
    const claimsYes = [`This is ${a.label.toLowerCase()} (${a.confidence.toLowerCase()} confidence on current evidence)`];
    const claimsNo = [];
    if (!["PLAYER_ISSUED", "PLAYER_WORN", "GAME_WORN"].includes(a.supported)) claimsNo.push("It was issued to any particular player");
    if (!["PLAYER_WORN", "GAME_WORN"].includes(a.supported)) claimsNo.push("It was worn by any player");
    if (a.supported !== "GAME_WORN") claimsNo.push("It was used in a specific game");
    if (!ref || ref.match_level !== "EXACT_PHOTO_MATCH") claimsNo.push("The reference image shows this exact physical item");
    const wished = state.me && !state.me.anonymous;
    app.innerHTML = `<section class="exhibit-head"><div class="wrap">
      <div class="crumbs muted"><a href="#/shop">Shop</a> / <a href="#/shop?department=${esc(p.department)}">${esc(p.department_name)}</a>${p.organisation_id ? ` / <a href="#/team/${esc(p.organisation_id)}">${esc(p.team_or_school)}</a>` : ""}</div>
      <div>${badge(a.supported, a.label)} ${p.is_demo ? badge("demo", "Demo exhibit, not for sale") : ""} <span class="mono muted">SKU ${esc(p.id)}</span></div>
      <h1 class="display" style="margin-top:10px">${esc(p.title)}</h1>
    </div></section>
    <div class="wrap">
      <div class="compare">
        <div class="panel ${skin}" style="box-shadow:none">
          <header><span class="mono">Left · the item offered</span><span class="badge b-demo">${esc(p.media.find((m) => m.side === "ITEM")?.match_label || "")}</span></header>
          <div class="frame">${art(p.art, 300)}</div>
          <div class="caption">${esc(p.media.find((m) => m.side === "ITEM")?.caption || "")}</div></div>
        <div class="panel">
          <header><span class="mono">Right · historical reference</span><span class="badge b-LICENSED_RETAIL">${esc(ref ? ref.match_label : "No reference")}</span></header>
          <div class="frame">${ref && ref.displayable && ref.url ? `<img src="${esc(ref.url)}" alt="${esc(ref.caption)}">`
            : `<div class="ref-pending"><div><div class="mono">Reference pending rights clearance</div><p>We only show archive photography we have the right to use.${ref && ref.url_link_only ? ` <a href="${esc(ref.url_link_only)}" rel="noopener" target="_blank">View source</a>` : ""}</p></div></div>`}</div>
          <div class="caption">${esc(ref ? ref.caption : "")}</div></div>
      </div>
      <div class="exhibit-body">
        <div class="panel plaque">
          <h3>The team</h3><p>${esc(p.story.team || "–")}</p>
          <h3>The era</h3><p>${esc(p.story.era || "–")}</p>
          <h3>The player connection</h3><p>${esc(p.player_connection || "No player connection is claimed.")}</p>
          <h3>The design</h3><p>${esc(p.story.design || "–")}</p>
          <h3>Rarity</h3><p>${esc(p.story.rarity || "–")}</p>
          <h3>Why collectors value it</h3><p>${esc(p.story.why_collect || "–")}</p>
          ${p.story.vs_retail ? `<h3>Versus retail</h3><p>${esc(p.story.vs_retail)}</p>` : ""}
          <h3>Provenance record</h3><ul>${evidence || "<li>No evidence recorded</li>"}</ul>
          <h3>Chain of custody</h3><ul class="timeline">${p.custody.map((c) => `<li><b>${esc(c.event)}</b> · ${esc(c.holder)}${c.happened_on ? ` · ${esc(c.happened_on)}` : ""}${c.documented ? " · documented" : " · undocumented"}</li>`).join("")}</ul>
          <h3>What this listing claims</h3><ul class="claims">${claimsYes.map((c) => `<li class="y">${esc(c)}</li>`).join("")}</ul>
          <h3>What it does not claim</h3><ul class="claims">${claimsNo.map((c) => `<li class="n">${esc(c)}</li>`).join("")}</ul>
          ${a.next_evidence.length ? `<p class="muted" style="margin-top:10px">To upgrade: ${esc(a.next_evidence.join(" · "))}</p>` : ""}
        </div>
        <aside><div class="panel buybox">
          <div class="mono muted">${p.is_demo ? "Illustrative price" : "Price"}</div><div class="price">${money(p.price_aud)}</div>
          <dl class="facts" style="margin:12px 0">
            <dt>Team</dt><dd>${esc(p.team_or_school || "–")}</dd><dt>Season</dt><dd>${esc(p.season || "–")}</dd>
            <dt>Item</dt><dd>${esc((p.item_type || "").replace(/_/g, " ").toLowerCase())}</dd><dt>Size</dt><dd>${esc(p.size || "–")}</dd>
            <dt>Condition</dt><dd>${esc((p.condition_grade || "").replace(/_/g, " ").toLowerCase())}</dd><dt>Source</dt><dd>${esc(p.ownership.toLowerCase())}</dd></dl>
          <button class="btn accent" style="width:100%" ${p.purchasable ? "" : "disabled"} id="buy">${p.purchasable ? "Add to cart" : esc(p.availability)}</button>
          <button class="btn alt" style="width:100%;margin-top:8px" id="wish">${wished ? "Save to wishlist" : "Sign in to save"}</button>
          <div class="out"></div>
          <div class="notice">${esc(p.description || "")}</div>
          <p class="muted" style="font-size:.8rem">Independent reseller. Not affiliated with or endorsed by the NBA, NCAA, any team, player or manufacturer.</p>
        </div></aside>
      </div>
    </div>`;
    $("#wish").addEventListener("click", async () => {
      if (!wished) { location.hash = "#/account"; return; }
      try { await api("/wishlist/" + p.id, { method: "POST" }); $(".buybox .out").innerHTML = `<div class="msg ok">Saved to your wishlist.</div>`; }
      catch (e) { $(".buybox .out").innerHTML = `<div class="msg err">${esc(e.message)}</div>`; }
    });
  }

  async function teams(r) {
    const all = await api("/teams");
    const league = r.q.get("league") || "NBA";
    const list = all.filter((t) => t.league_id === league);
    app.innerHTML = `<section class="block"><div class="wrap">
      <div class="section-head"><h2 class="display">${league === "NBA" ? "All 30 franchises" : "College programmes"}</h2>
        <div class="chips" style="margin:0"><a class="chip ${league === "NBA" ? "on" : ""}" href="#/teams?league=NBA">NBA</a><a class="chip ${league === "NCAA" ? "on" : ""}" href="#/teams?league=NCAA">NCAA</a></div></div>
      <div class="depts">${list.map((t) => `<a class="dept" href="#/team/${esc(t.id)}"><span class="mono muted count">${t.products || ""}</span>
        <div class="mono muted">${esc(t.conference || "")}${t.division ? " · " + esc(t.division) : ""}</div><h3>${esc(t.name)}</h3>
        <p>${esc(t.iconic_era || t.nickname || "")}</p>${t.australian_connection ? `<p class="mono" style="margin-top:6px;color:var(--accent)">AUS · ${esc(t.australian_connection.split(";").slice(0, 2).join(";"))}</p>` : ""}</a>`).join("")}</div>
    </div></section>`;
  }

  async function team(r) {
    const t = await api("/teams/" + encodeURIComponent(r.arg));
    app.innerHTML = `<section class="block"><div class="wrap">
      <div class="crumbs muted"><a href="#/teams?league=${esc(t.league_id)}">Teams</a> / ${esc(t.name)}</div>
      <h1 class="display" style="font-size:clamp(2.4rem,7vw,5rem)">${esc(t.name)}</h1>
      <p class="mono muted">${esc([t.conference, t.division, t.city].filter(Boolean).join(" · "))}</p>
      <div class="exhibit-body" style="margin-top:20px">
        <div class="panel plaque"><h3>Iconic equipment era</h3><p>${esc(t.iconic_era || "Research in progress")}</p>
          <h3>Recent results</h3><p>${esc(t.recent_success || "Not yet researched")}</p>
          <h3>Australian connection</h3>${t.players.length ? `<ul>${t.players.map((p) => `<li><a href="#/player/${esc(p.id)}">${esc(p.name)}</a> ${p.seasons ? esc(p.seasons) : ""}${p.is_current ? " · current" : ""}${p.champion ? " · champion" : ""} <span class="mono muted">${esc(p.verification)}</span></li>`).join("")}</ul>` : "<p>No sourced Australian connection recorded.</p>"}
        </div>
        <div class="panel plaque"><h3>Sources</h3><ul style="font-size:.85rem">${t.sources.map((s) => `<li><a href="${esc(s.url)}" rel="noopener" target="_blank">${esc(s.supports || s.url)}</a></li>`).join("") || "<li>None yet</li>"}</ul></div>
      </div>
      <div class="section-head" style="margin-top:30px"><h2 class="display">Exhibits</h2></div>
      <div class="grid">${t.products.map(card).join("") || `<p class="muted">No exhibits yet for this team.</p>`}</div>
    </div></section>`;
  }

  async function aussies() {
    const ps = await api("/players");
    const groups = { CURRENT_NBA: "Current NBA (2026-27)", FORMER_NBA: "Former NBA", FORMER_NCAA: "College alumni (NCAA)" };
    app.innerHTML = `<section class="block"><div class="wrap">
      <div class="section-head"><h2 class="display">The Australian connection</h2><span class="mono muted">${ps.length} players · every row sourced</span></div>
      <p class="muted">Verification shows how strong the source is. PARTIAL means some details came from secondary summaries and are being re-checked.</p>
      ${Object.entries(groups).map(([k, label]) => {
        const g = ps.filter((p) => p.status === k); if (!g.length) return "";
        return `<h3 class="display" style="font-size:1.6rem;margin:26px 0 10px">${label}</h3><div class="table-wrap"><table class="data"><thead><tr><th>Player</th><th>Teams / schools</th><th>College</th><th>Verification</th></tr></thead><tbody>
          ${g.map((p) => `<tr><td><a href="#/player/${esc(p.id)}">${esc(p.name)}</a></td><td>${esc(p.stints || "")}</td><td>${esc(p.college || "")}</td><td><span class="mono">${esc(p.verification)}</span></td></tr>`).join("")}</tbody></table></div>`;
      }).join("")}
    </div></section>`;
  }

  async function player(r) {
    const p = await api("/players/" + encodeURIComponent(r.arg));
    app.innerHTML = `<section class="block"><div class="wrap">
      <div class="crumbs muted"><a href="#/aussies">Aussie Links</a> / ${esc(p.name)}</div>
      <h1 class="display" style="font-size:clamp(2.4rem,7vw,5rem)">${esc(p.name)}</h1>
      <p class="mono muted">${esc((p.status || "").replace(/_/g, " "))} · ${esc(p.verification)}</p>
      <div class="exhibit-body"><div class="panel plaque"><h3>Career references</h3><ul>${p.stints.map((s) => `<li>${s.organisation_id ? `<a href="#/team/${esc(s.organisation_id)}">${esc(s.organisation_name)}</a>` : esc(s.organisation_name)} ${esc(s.seasons || "")}${s.is_current ? " · current" : ""}${s.champion ? " · champion" : ""}</li>`).join("")}</ul>
        ${p.achievements ? `<h3>Achievements</h3><p>${esc(p.achievements)}</p>` : ""}
        <p class="notice">Player references describe history. They never mean a product was issued to or worn by this player unless the product's own evidence says so.</p></div>
        <div class="panel plaque"><h3>Sources</h3><ul style="font-size:.85rem">${p.sources.map((s) => `<li><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.url)}</a></li>`).join("")}</ul></div></div>
      <div class="section-head" style="margin-top:30px"><h2 class="display">Exhibits from their teams</h2></div>
      <div class="grid">${p.products.map(card).join("") || `<p class="muted">None yet.</p>`}</div>
    </div></section>`;
  }

  async function vault() {
    const items = await api("/products?department=TEARAWAY_VAULT");
    app.innerHTML = `<section class="vault-hero"><div class="wrap">
      <div class="mono muted">The signature collection</div><h1 class="display">The Tearaway<br>Vault</h1>
      <p class="lede" style="margin:0 auto;max-width:620px">Full side-snap warmup pants: the sound of a player checking in. Here's how they're built, how team issue differs from what was in shops, and the pieces we've documented.</p>
      <button class="btn accent" id="play" style="margin-top:20px">▶ Remember the sound?</button>
    </div></section>
    <section class="block"><div class="wrap snap-demo">
      <button class="icon-btn snap-stage" id="stage" aria-label="Tear away the warmup pants">${art({ g: "pants", c1: era() === "og" ? "#00838f" : "#2a3442", c2: era() === "og" ? "#e2611b" : "#c1ed57", c3: "#f8f5eb", pin: era() === "og" }, 360)}</button>
      <div><h2 class="display" style="font-size:2.4rem">Construction guide</h2>
        <dl class="facts">
          <dt>Side snaps</dt><dd>A full run of press-studs down each outer seam lets the pants come off over shoes in one pull.</dd>
          <dt>Placket</dt><dd>A fabric strip behind the snaps takes the strain and keeps them from pulling through.</dd>
          <dt>Waist</dt><dd>Elastic or drawcord waist; pairs are often worn over game shorts.</dd>
          <dt>Shell and lining</dt><dd>Woven shells (often polyester or nylon) in 1990s sets, with mesh or tricot linings; modern sets use lighter technical knits.</dd>
          <dt>Pro sizing</dt><dd>Team issue often carries length-adjusted sizes such as XL+2 or 3XLT for tall players. Unusual sizing is a reason to inspect, not proof.</dd>
          <dt>Labels</dt><dd>Team-issue tags, internal codes or sewn name and number tags are recorded as evidence when present and verified.</dd>
        </dl>
        <p class="muted" style="font-size:.85rem">Materials vary by maker and season. We only state the construction of a specific item when it has been inspected and photographed.</p></div>
    </div></section>
    <section class="block" style="border-top:var(--card-border)"><div class="wrap">
      <h2 class="display" style="font-size:2.4rem;margin-bottom:14px">Team issue versus retail</h2>
      <div class="table-wrap"><table class="compare-table"><thead><tr><th>What we check</th><th>Team-issued pair (when verified)</th><th>Typical retail pair</th></tr></thead><tbody>
        <tr><td>Sizing</td><td>May include length-adjusted pro sizes</td><td>Standard S–XXL</td></tr>
        <tr><td>Labelling</td><td>Team-issue or internal tags; sometimes name/number tags</td><td>Retail hangtags, barcodes and retail care labels</td></tr>
        <tr><td>Where it came from</td><td>Team, university or official partner release, documented</td><td>Retail store or licensed distributor</td></tr>
        <tr><td>Design</td><td>Season-specific on-court spec</td><td>Can match the on-court look, or be a fan version</td></tr>
        <tr><td>How we label it</td><td>Team-Issued / Vintage Team Issue</td><td>Licensed Retail (Logo Archive)</td></tr>
      </tbody></table></div>
      <p class="muted" style="font-size:.85rem">These are the differences we look for, not guarantees. Some retail lines are named "team issue" in shops; the name alone proves nothing.</p>
    </div></section>
    <section class="block" style="border-top:var(--card-border)"><div class="wrap">
      <h2 class="display" style="font-size:2.4rem;margin-bottom:14px">Historic comparisons</h2>
      <div class="era-strip">
        <div class="panel"><div class="yr">1990s</div><p>Oversized woven sets, bold colour blocking and pinstripes, full snap runs. The era that made the sound famous.</p></div>
        <div class="panel"><div class="yr">2000s</div><p>Bulkier silhouettes, embroidered wordmarks, mesh linings. The Kobe-Shaq and Duncan-era warmups.</p></div>
        <div class="panel"><div class="yr">2010s</div><p>Slimmer technical knits and more seasonal variations, including special-event sets.</p></div>
        <div class="panel"><div class="yr">Now</div><p>Lightweight performance fabrics and many partial-snap or zip designs alongside full tearaways.</p></div>
      </div>
      <p class="muted" style="font-size:.85rem">General era observations for storytelling. Specific claims about any team's set are documented per item.</p>
    </div></section>
    <section class="block" style="border-top:var(--card-border)"><div class="wrap">
      <div class="section-head"><h2 class="display">The visual archive</h2><span class="mono muted">${items.length} documented pairs (demo)</span></div>
      <div class="grid">${items.map(card).join("")}</div>
    </div></section>`;
    const stage = $("#stage");
    const go = () => { snapSound(9); stage.classList.toggle("torn"); };
    stage.addEventListener("click", go); $("#play").addEventListener("click", go);
  }

  async function exchange() {
    const tiers = await api("/seller-tiers");
    const ev = [["OFFICIAL_SOURCE_PURCHASE", "Receipt from an official team or university sale"], ["TEAM_LOA", "Team or official partner letter of authenticity"],
      ["AUTHENTICATOR_CERT", "Independent authenticator certificate"], ["CHAIN_OF_CUSTODY", "Documented chain of custody"],
      ["TEAM_ISSUE_TAG", "Team-issue tags"], ["TALL_OR_PRO_SIZING", "Pro sizing (e.g. XL+2)"], ["PLAYER_NAME_TAG", "Sewn player name/number tag"],
      ["WEAR_LOA", "Letter confirming the player wore it"], ["PHOTO_MATCH", "Independent photo-match"], ["GENUINE_MANUFACTURER", "Legit-checked genuine product"]];
    app.innerHTML = `<section class="block"><div class="wrap">
      <div class="section-head"><h2 class="display">The Collector Exchange</h2></div>
      <div class="exhibit-body"><div class="panel plaque">
        <h3>Consign a piece</h3><p class="muted">We authenticate before anything is listed. Proposed commission: 25% (20% on sales over A$1,000), confirmed in a written agreement. Nothing is accepted until we've reviewed your evidence and we've both signed.</p>
        <form class="form" id="consign">
          <div class="two"><label>Your name<input name="applicant_name" required maxlength="120"></label><label>Email<input name="applicant_email" type="email" required></label></div>
          <label>Describe the item<textarea name="item_description" rows="3" required maxlength="2000" placeholder="Team, season, item type, size, condition"></textarea></label>
          <div class="two"><label>Team or school<input name="team_or_school" maxlength="80"></label>
            <label>Item type<select name="item_type"><option value="TEARAWAY_PANTS">Tearaway pants</option><option value="WARMUP_JACKET">Warmup jacket</option><option value="SHOOTING_SHIRT">Shooting shirt</option><option value="JERSEY">Jersey</option><option value="SHOES">Shoes</option><option value="OTHER">Other</option></select></label></div>
          <div class="two"><label>Season (if known)<input name="era" placeholder="e.g. 1997-98" maxlength="10"></label><label>Asking price (A$)<input name="asking_price_aud" type="number" min="0" step="1"></label></div>
          <label>How did you get it?<textarea name="provenance_story" rows="3" maxlength="4000"></textarea></label>
          <fieldset style="border:0;padding:0;margin:0"><legend style="font-weight:600;font-size:.88rem;margin-bottom:6px">What evidence do you hold?</legend>
            ${ev.map(([c, l]) => `<label class="check"><input type="checkbox" name="evidence" value="${c}"> ${l}</label>`).join("")}</fieldset>
          <button class="btn accent" type="submit">Submit for review</button><div class="out"></div></form>
      </div>
      <aside><div class="panel plaque"><h3>Seller onboarding</h3>
        ${Object.entries(tiers).map(([k, t]) => `<p><b>${esc(k.replace(/_/g, " "))}</b><br><span class="muted">${esc(t.can.join("; "))}</span>${t.requires.length ? `<br><span class="mono" style="font-size:.7rem">Needs: ${esc(t.requires.join(", ").replace(/_/g, " "))}</span>` : ""}</p>`).join("")}
        <p class="notice">The open peer-to-peer marketplace launches only after seller verification, buyer protection and a legal review are in place.</p></div></aside></div>
    </div></section>`;
    $("#consign").addEventListener("submit", async (e) => {
      e.preventDefault(); const f = e.target; const fd = new FormData(f);
      const body = Object.fromEntries([...fd.entries()].filter(([k]) => k !== "evidence")); body.evidence_offered = fd.getAll("evidence");
      try {
        const r = await api("/consignments", { method: "POST", body });
        $(".out", f).innerHTML = `<div class="msg ok">Application #${r.id} received. Preliminary view: ${esc(r.preliminary_assessment.label)}. ${esc(r.message)}</div>`; f.reset();
      } catch (err) { $(".out", f).innerHTML = `<div class="msg err">${esc(err.message)}</div>`; }
    });
  }

  async function locker() {
    const posts = await api("/wanted");
    app.innerHTML = `<section class="block"><div class="wrap">
      <div class="section-head"><h2 class="display">The Locker Room</h2><span class="mono muted">Wanted board · collector stories</span></div>
      <div class="exhibit-body"><div>
        <h3 class="display" style="font-size:1.6rem">Wanted board</h3>
        <div class="table-wrap"><table class="data" style="min-width:0"><thead><tr><th>Collector</th><th>Wants</th><th>Budget</th></tr></thead><tbody>
          ${posts.map((p) => `<tr><td>${esc(p.display_name)}</td><td><b>${esc(p.team_or_school || "")}</b> ${esc(p.item_type || "")} ${esc(p.era || "")}<br>${esc(p.description)}</td><td>${p.budget_aud_cents ? money(p.budget_aud_cents / 100) : "–"}</td></tr>`).join("") || `<tr><td colspan="3" class="muted">No approved posts yet. Be the first.</td></tr>`}
        </tbody></table></div>
        <h3 class="display" style="font-size:1.6rem;margin-top:26px">Community plan</h3>
        <ul><li>Monthly collector spotlights: the story behind one piece, told by its owner.</li><li>Australian NBL and NCAA alumni nights with local collector groups.</li>
          <li>Wanted-item matching: our hunters see every approved post.</li><li>Moderated, real-name collector exchange only after seller verification.</li></ul>
      </div>
      <aside><div class="panel plaque"><h3>Post a wanted item</h3>
        <form class="form" id="wanted">
          <label>Display name<input name="display_name" required maxlength="60"></label>
          <div class="two"><label>Team or school<input name="team_or_school" maxlength="80"></label><label>Era<select name="era"><option value="OG">OG</option><option value="CURRENT">Current</option></select></label></div>
          <label>Item<select name="item_type"><option>Tearaway pants</option><option>Warmup jacket</option><option>Shooting shirt</option><option>Jersey</option><option>Shoes</option><option>Other</option></select></label>
          <label>Details<textarea name="description" rows="3" required maxlength="1000"></textarea></label>
          <label>Budget (A$)<input name="budget_aud" type="number" min="0"></label>
          <button class="btn accent" type="submit">Post (moderated)</button><div class="out"></div></form></div></aside></div>
    </div></section>`;
    $("#wanted").addEventListener("submit", async (e) => {
      e.preventDefault(); const f = e.target;
      try { const r = await api("/wanted", { method: "POST", body: Object.fromEntries(new FormData(f)) }); $(".out", f).innerHTML = `<div class="msg ok">${esc(r.message)}</div>`; f.reset(); }
      catch (err) { $(".out", f).innerHTML = `<div class="msg err">${esc(err.message)}</div>`; }
    });
  }

  async function standards() {
    const s = await api("/standards");
    app.innerHTML = `<section class="block"><div class="wrap">
      <h2 class="display" style="font-size:clamp(2rem,6vw,3.6rem)">Authentication standards</h2>
      <p class="lede">Authentic on court means verified team issue. We classify every item by the strongest claim its evidence supports, never by what a seller says.</p>
      <h3 class="display" style="font-size:1.5rem;margin-top:24px">Classes</h3>
      <div class="chips">${Object.entries(s.classes).map(([k, v]) => badge(k, v)).join(" ")}</div>
      <h3 class="display" style="font-size:1.5rem;margin-top:24px">Evidence we record</h3>
      <div class="table-wrap"><table class="data" style="min-width:0"><thead><tr><th>Evidence</th><th>Tier</th><th>Meaning</th></tr></thead><tbody>
        ${Object.entries(s.evidence).map(([k, v]) => `<tr><td class="mono">${esc(k)}</td><td>${esc({ A: "Institutional", B: "Construction / custody", P: "Player allocation", C: "Use", D: "Design reference", K: "Kicks", G: "Genuine", X: "Not evidence" }[v.tier])}</td><td>${esc(v.meaning)}</td></tr>`).join("")}</tbody></table></div>
      <h3 class="display" style="font-size:1.5rem;margin-top:24px">How the rules work</h3>
      <ul><li><b>Team-Issued</b> needs official provenance or an authenticator, or a documented chain of custody plus construction evidence, or a team-issue tag plus two construction markers (medium confidence).</li>
        <li><b>Player-Issued</b> adds a sewn name tag, an allocation document or an official letter naming the player.</li>
        <li><b>Player-Worn</b> adds a wear letter. <b>Game-Worn</b> needs an independent photo-match or a letter naming the game.</li>
        <li>Seasons starting 2009 or earlier are labelled <b>Vintage Team Issue</b>.</li>
        <li>Counterfeit signs, unclear title, possible theft or restricted college athlete items block a listing outright.</li>
        <li>Marketing copy is checked automatically: words like "game-worn" or "team-issued" are refused when the evidence doesn't support them.</li></ul>
      <h3 class="display" style="font-size:1.5rem;margin-top:24px">Reference images</h3>
      <ul>${Object.entries(s.reference_levels).map(([k, v]) => `<li><span class="mono">${esc(k)}</span>: ${esc(v)}</li>`).join("")}</ul>
    </div></section>`;
  }

  async function account() {
    await refreshMe();
    if (state.me && !state.me.anonymous) {
      const wl = await api("/wishlist");
      app.innerHTML = `<section class="block"><div class="wrap"><div class="section-head"><h2 class="display">Hi ${esc(state.me.display_name || "")}</h2>
        <button class="btn alt" id="logout">Sign out</button></div>
        ${state.me.role === "ADMIN" ? `<p><a class="btn accent" href="#/admin">Open admin dashboard</a></p>` : ""}
        <h3 class="display" style="font-size:1.6rem">Your wishlist</h3><div class="grid">${wl.map(card).join("") || `<p class="muted">Nothing saved yet.</p>`}</div></div></section>`;
      $("#logout").addEventListener("click", async () => { await api("/auth/logout", { method: "POST" }); state.me = null; render(); });
      return;
    }
    app.innerHTML = `<section class="block"><div class="wrap" style="max-width:860px"><div class="exhibit-body" style="grid-template-columns:1fr 1fr">
      <div class="panel plaque"><h3>Sign in</h3><form class="form" id="login"><label>Email<input type="email" name="email" required></label><label>Password<input type="password" name="password" required></label><button class="btn accent">Sign in</button><div class="out"></div></form></div>
      <div class="panel plaque"><h3>Create an account</h3><form class="form" id="register"><label>Name<input name="display_name" maxlength="60"></label><label>Email<input type="email" name="email" required></label><label>Password (8+ characters)<input type="password" name="password" minlength="8" required></label><button class="btn">Create account</button><div class="out"></div></form></div>
    </div></div></section>`;
    for (const id of ["login", "register"]) {
      $("#" + id).addEventListener("submit", async (e) => {
        e.preventDefault(); const f = e.target;
        try { await api("/auth/" + id, { method: "POST", body: Object.fromEntries(new FormData(f)) }); await refreshMe(); render(); }
        catch (err) { $(".out", f).innerHTML = `<div class="msg err">${esc(err.message)}</div>`; }
      });
    }
  }

  async function refreshMe() {
    try { state.me = await api("/me"); } catch (e) { state.me = null; }
    $("#nav-account").textContent = state.me && !state.me.anonymous ? "Account" : "Sign in";
  }

  // ------------------------------------------------------------ admin
  const tbl = (cols, data) => `<div class="table-wrap"><table class="data"><thead><tr>${cols.map((c) => `<th>${esc(c[0])}</th>`).join("")}</tr></thead><tbody>
    ${data.map((r) => `<tr>${cols.map((c) => `<td>${c[1](r)}</td>`).join("")}</tr>`).join("") || `<tr><td colspan="${cols.length}" class="muted">No rows</td></tr>`}</tbody></table></div>`;
  const pill = (cls, v) => `<span class="pill ${cls}">${esc(String(v ?? "").replace(/_/g, " "))}</span>`;

  async function admin(r) {
    await refreshMe();
    if (!state.me || state.me.role !== "ADMIN") {
      app.innerHTML = `<section class="block"><div class="wrap"><h2 class="display">Team admin</h2><p>Sign in with the founder account to open the dashboard.</p><a class="btn accent" href="#/account">Sign in</a></div></section>`;
      return;
    }
    const tab = r.arg || "overview";
    const tabs = [["overview", "Overview"], ["sourcing", "Sourcing"], ["search", "Search plan"], ["crm", "CRM"], ["outreach", "Outreach"], ["launch", "Launch 30"],
      ["budget", "Budget"], ["products", "Products"], ["consign", "Consignments"], ["wanted", "Wanted"], ["demand", "Demand"], ["channels", "Channels"]];
    app.innerHTML = `<section class="block"><div class="wrap"><div class="section-head"><h2 class="display">Operations dashboard</h2><span class="mono muted">Signed in as ${esc(state.me.email)}</span></div>
      <div class="tabs">${tabs.map(([k, l]) => `<button class="${k === tab ? "on" : ""}" data-tab="${k}">${l}</button>`).join("")}</div><div id="pane" class="loading">Loading…</div></div></section>`;
    app.querySelectorAll("[data-tab]").forEach((b) => b.addEventListener("click", () => (location.hash = "#/admin/" + b.dataset.tab)));
    const pane = $("#pane"); pane.classList.remove("loading");
    await (adminTabs[tab] || adminTabs.overview)(pane, r.q);
  }

  const adminTabs = {
    async overview(pane) {
      const o = await api("/admin/overview");
      const k = (v, l) => `<div class="panel kpi"><div class="v">${esc(v)}</div><div class="l">${esc(l)}</div></div>`;
      pane.innerHTML = `<div class="kpis">
        ${k(`${o.sourcing.qualified}/${o.sourcing.target}`, "Qualified opportunities today (real listings)")}
        ${k(o.sourcing.evaluated, "Real listings evaluated")}
        ${k(`${o.launch.ready_total}/30`, "Launch products ready")}
        ${k(money(o.budget.committed_aud), "Acquisitions approved")}
        ${k(money(o.budget.remaining_aud), "Headroom under A$2,000")}
        ${k(o.registers.organisations, "Organisations in register")}
        ${k(o.registers.players, "Australian players")}
        ${k(o.registers.sources, "Cited sources")}</div>
        <div class="exhibit-body"><div class="panel plaque"><h3>Sourcing shortfall</h3><p>${o.sourcing.shortfall} short of the daily target of ${o.sourcing.target}. ${esc(o.sourcing.note)}</p>
          <p>Investigate: ${o.sourcing.investigate} · Needs evidence: ${o.sourcing.needs_evidence ?? 0} · Watch: ${o.sourcing.watch} · Rejected: ${o.sourcing.rejected}</p>
          <h3>Contacts by tier</h3><p>${o.contacts.map((c) => pill("t-" + c.tier, c.tier) + " " + c.n).join(" &nbsp; ")}</p>
          <h3>Outreach</h3><p>${o.outreach.map((c) => `${esc(c.status)}: ${c.n}`).join(" · ") || "No drafts yet"} · <b>No message has been sent by this system.</b></p></div>
        <div class="panel plaque"><h3>Recent agent runs</h3>${o.agent_runs.length ? `<ul style="font-size:.85rem">${o.agent_runs.map((a) => `<li><b>${esc(a.agent)}</b> ${esc(a.started_at)} ${a.ok ? "✓" : "✕"}<br><span class="muted">${esc(a.summary || "")}</span></li>`).join("")}</ul>` : "<p class='muted'>No runs recorded. Run <span class='mono'>python3 -m agents.run all</span>.</p>"}</div></div>`;
    },
    async sourcing(pane, q) {
      const params = new URLSearchParams(q); const data = await api("/admin/opportunities?" + params);
      pane.innerHTML = `<form class="toolbar" id="of"><input type="search" name="q" placeholder="Search" value="${esc(q.get("q") || "")}">
        <select name="recommendation"><option value="">Any recommendation</option>${["PROPOSE_TO_FOUNDER", "INVESTIGATE", "WATCH", "NEEDS_EVIDENCE", "REJECT"].map((v) => `<option ${q.get("recommendation") === v ? "selected" : ""}>${v}</option>`).join("")}</select>
        <select name="risk"><option value="">Any risk</option>${"ABCDE".split("").map((v) => `<option ${q.get("risk") === v ? "selected" : ""}>${v}</option>`).join("")}</select>
        <input name="max_landed" type="number" placeholder="Max landed A$" value="${esc(q.get("max_landed") || "")}">
        <select name="sort">${[["score", "Rank by score"], ["margin", "Margin"], ["landed", "Landed cost"], ["demand", "Demand"]].map(([v, l]) => `<option value="${v}" ${q.get("sort") === v ? "selected" : ""}>${l}</option>`).join("")}</select>
        <label class="check"><input type="checkbox" name="live" value="1" ${q.get("live") ? "checked" : ""}> Real only</label><button class="btn">Apply</button>
        <button type="button" class="btn alt" id="reeval">Re-evaluate all</button></form>
        ${tbl([["#", (r) => esc(r.id)], ["Item", (r) => `<a href="${esc(r.listing_url)}" target="_blank" rel="noopener">${esc(r.title)}</a><br><span class="muted">${esc(r.team_or_school || "")} · ${esc(r.platform || "")}${r.is_demo ? " · DEMO" : ""}${r.live_verified ? "" : " · not loaded live"}</span>`],
          ["Listed", (r) => `${esc(r.currency)} ${(r.listed_price_cents / 100).toFixed(2)}`], ["Landed A$", (r) => r.landed_cost_aud_cents ? (r.landed_cost_aud_cents / 100).toFixed(2) : "–"],
          ["Resale A$", (r) => r.est_resale_aud_cents ? (r.est_resale_aud_cents / 100).toFixed(0) : "no verified comps"], ["Margin", (r) => r.gross_margin_pct != null ? r.gross_margin_pct + "%" : "–"],
          ["Class", (r) => badge(r.supported_classification)], ["Claimed", (r) => esc(r.claimed_classification || "")], ["Demand", (r) => r.demand_score ?? "–"],
          ["Score", (r) => r.deal_score], ["Risk", (r) => r.risk_grade], ["Recommendation", (r) => pill("r-" + r.recommendation, r.recommendation)],
          ["Why", (r) => `<span style="font-size:.78rem">${esc((r.rejection_reasons || []).join(" · "))}</span>`]], data)}`;
      $("#of").addEventListener("submit", (e) => { e.preventDefault(); const p = new URLSearchParams(); for (const [k, v] of new FormData(e.target)) if (v) p.set(k, v); location.hash = "#/admin/sourcing?" + p; });
      $("#reeval").addEventListener("click", async () => { await api("/admin/evaluate", { method: "POST" }); render(); });
    },
    async search(pane) {
      const d = await api("/admin/search-plan");
      pane.innerHTML = `<p class="muted">${esc(d.note)} Priority teams from the demand model: ${esc(d.generated_for.join(", "))}.</p>
        ${tbl([["Team", (r) => esc(r.team)], ["Query", (r) => `<span class="mono">${esc(r.query)}</span>`], ["Open search", (r) => Object.entries(r.links).map(([k, u]) => `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(k)}</a>`).join(" · ")]], d.plan)}`;
    },
    async crm(pane, q) {
      const kind = q.get("kind") || ""; const data = await api("/admin/crm" + (kind ? "?kind=" + kind : ""));
      pane.innerHTML = `<div class="chips">${[["", "All"], ["NBA_TEAM", "NBA"], ["NCAA_PROGRAMME", "NCAA"], ["SUPPLIER", "Suppliers"], ["AUCTION_HOUSE", "Auction houses"], ["AUTHENTICATOR", "Authenticators"], ["UNIVERSITY_SURPLUS", "University surplus"]].map(([k, l]) => `<a class="chip ${k === kind ? "on" : ""}" href="#/admin/crm?kind=${k}">${l}</a>`).join("")}</div>
        ${tbl([["Organisation", (r) => `<a href="#" data-org="${esc(r.id)}">${esc(r.name)}</a><br><span class="muted">${esc(r.conference || "")} ${esc(r.division || "")}</span>`], ["Type", (r) => esc(r.kind.replace(/_/g, " "))],
          ["Best contact", (r) => r.best_tier ? `${pill("t-" + r.best_tier, r.best_tier)}<br><span style="font-size:.78rem;word-break:break-all">${esc(r.best_contact || "")}</span>` : `<span class="muted">none researched</span>`],
          ["Aus connection", (r) => `<span style="font-size:.8rem">${esc(r.australian_connection || "")}</span>`], ["Purchasing route", (r) => `<span style="font-size:.78rem">${esc((r.approved_purchasing_process || "").slice(0, 160))}</span>`],
          ["Status", (r) => esc(r.status || "NOT_CONTACTED")], ["Follow-up", (r) => esc(r.follow_up_date || "")], ["Msgs", (r) => `${r.messages}/${r.sent} sent`]], data)}
        <div id="orgpane"></div>`;
      pane.querySelectorAll("[data-org]").forEach((a) => a.addEventListener("click", async (e) => { e.preventDefault(); await orgDetail(a.dataset.org); }));
    },
    async outreach(pane) {
      const d = await api("/admin/outreach");
      pane.innerHTML = `<p class="notice">Drafts only. Approval records the founder's sign-off; this system has no ability to send email. Follow-ups are drafted at day 14 and 28 only after a real send is recorded.</p>
        ${tbl([["#", (r) => r.id], ["Organisation", (r) => `<a href="#" data-org="${esc(r.organisation_id)}">${esc(r.name)}</a>`], ["Step", (r) => r.sequence_step], ["Subject", (r) => esc(r.subject)], ["Status", (r) => esc(r.status)], ["Approved by", (r) => esc(r.approved_by || "")]], d)}<div id="orgpane"></div>`;
      pane.querySelectorAll("[data-org]").forEach((a) => a.addEventListener("click", async (e) => { e.preventDefault(); await orgDetail(a.dataset.org); }));
    },
    async launch(pane) {
      const t = await api("/admin/launch");
      pane.innerHTML = `<div class="kpis">${Object.entries(t.target).map(([k, v]) => `<div class="panel kpi"><div class="v">${t.ready[k]}/${v}</div><div class="l">${k.toLowerCase()} ready</div></div>`).join("")}
        <div class="panel kpi"><div class="v">${t.launch_ready ? "YES" : "NO"}</div><div class="l">Launch gate passed</div></div></div><p class="muted">${esc(t.note)}</p>
        <div class="slotgrid">${t.slots.map((s) => `<div class="slot ${s.state}"><div class="mono">#${s.slot} · ${s.lane}</div><div>${esc(s.target_description)}</div><div class="mono muted">${s.state.replace(/_/g, " ")}</div></div>`).join("")}</div>`;
    },
    async budget(pane) {
      const b = await api("/admin/budget");
      pane.innerHTML = `<div class="kpis"><div class="panel kpi"><div class="v">${money(b.committed_aud)}</div><div class="l">Approved / committed</div></div>
        <div class="panel kpi"><div class="v">${money(b.proposed_aud)}</div><div class="l">Proposed (awaiting founder)</div></div><div class="panel kpi"><div class="v">${money(b.remaining_aud)}</div><div class="l">Headroom (strictly under A$2,000)</div></div></div>
        <p class="notice">${esc(b.note)}</p>
        ${tbl([["Category", (r) => esc(r.category)], ["Envelope", (r) => money(r.envelope_aud)], ["Committed", (r) => money(r.committed_aud)], ["Proposed", (r) => money(r.proposed_aud)],
          ["Use", (r) => `<div class="bar-meter"><span style="width:${Math.min(100, (r.committed_aud / r.envelope_aud) * 100)}%"></span></div>`]], b.categories)}`;
    },
    async products(pane) {
      const d = await api("/admin/products");
      pane.innerHTML = tbl([["SKU", (r) => esc(r.id)], ["Title", (r) => esc(r.title)], ["Status", (r) => esc(r.status)], ["Supported class", (r) => badge(r.classification)],
        ["Gate", (r) => r.gate.ready ? pill("r-PROPOSE_TO_FOUNDER", "READY") : `<span style="font-size:.78rem">${esc(r.gate.failed.join(", ").replace(/_/g, " "))}</span>`],
        ["Copy issues", (r) => `<span style="font-size:.78rem">${esc(r.gate.copy_issues.map((i) => `"${i.phrase}": ${i.problem}`).join(" · "))}</span>`]], d);
    },
    async consign(pane) {
      const d = await api("/admin/consignments");
      pane.innerHTML = tbl([["#", (r) => r.id], ["Applicant", (r) => `${esc(r.applicant_name)}<br><span class="muted">${esc(r.applicant_email)}</span>`], ["Item", (r) => esc(r.item_description)],
        ["Evidence offered", (r) => `<span class="mono" style="font-size:.72rem">${esc((JSON.parse(r.evidence_offered || "[]")).join(", "))}</span>`], ["Status", (r) => esc(r.status)],
        ["Action", (r) => `<select data-c="${r.id}"><option value="">Advance…</option>${({ SUBMITTED: ["EVIDENCE_REVIEW", "DECLINED"], EVIDENCE_REVIEW: ["ACCEPTED", "DECLINED"], ACCEPTED: ["AGREEMENT_SENT", "DECLINED"] }[r.status] || []).map((s) => `<option>${s}</option>`).join("")}</select>`]], d);
      pane.querySelectorAll("[data-c]").forEach((s) => s.addEventListener("change", async () => { if (!s.value) return; try { await api(`/admin/consignments/${s.dataset.c}/advance`, { method: "POST", body: { status: s.value } }); render(); } catch (e) { alert(e.message); } }));
    },
    async wanted(pane) {
      const d = await api("/admin/wanted");
      pane.innerHTML = tbl([["#", (r) => r.id], ["Name", (r) => esc(r.display_name)], ["Wants", (r) => esc(`${r.team_or_school || ""} ${r.item_type || ""}: ${r.description}`)], ["Status", (r) => esc(r.status)],
        ["Moderate", (r) => r.status === "PENDING_MODERATION" ? `<button class="btn" data-w="${r.id}" data-s="OPEN">Approve</button> <button class="btn alt" data-w="${r.id}" data-s="REJECTED">Reject</button>` : ""]], d);
      pane.querySelectorAll("[data-w]").forEach((b) => b.addEventListener("click", async () => { await api("/admin/wanted/" + b.dataset.w, { method: "POST", body: { status: b.dataset.s } }); render(); }));
    },
    async demand(pane) {
      const d = await api("/admin/demand");
      pane.innerHTML = `<p class="notice">Scores combine measured factors (cited, dated sources) and estimates. "Measured share" shows how much of each score rests on measured data; most is still estimate.</p>
        ${tbl([["Rank", (r) => r.rank], ["Organisation", (r) => esc(r.name)], ["Score /100", (r) => r.score], ["Measured share", (r) => r.measured_share_pct + "%"], ["Label", (r) => esc(r.label)],
          ["Measured factors", (r) => `<span style="font-size:.78rem">${esc(r.factors.filter((f) => f.basis === "MEASURED").map((f) => `${f.factor} ${f.score}: ${f.evidence}`).join(" · "))}</span>`]], d)}`;
    },
    async channels(pane) {
      const d = await api("/admin/channels");
      pane.innerHTML = tbl([["Channel", (r) => esc(r.name)], ["Type", (r) => esc(r.channel_type)], ["Sells", (r) => `<span style="font-size:.78rem">${esc((r.sells || "").slice(0, 180))}</span>`],
        ["Ships to AU", (r) => `<span style="font-size:.78rem">${esc(r.ships_to_au || "unknown")}</span>`], ["Published contact", (r) => `<span style="font-size:.78rem">${esc(r.published_contact || "")}</span>`],
        ["Fit", (r) => r.fit_score ?? "–"], ["Verification", (r) => esc(r.verification)]], d);
    },
  };

  async function orgDetail(oid) {
    const o = await api("/admin/crm/" + encodeURIComponent(oid));
    const box = $("#orgpane");
    box.innerHTML = `<div class="panel plaque" style="margin-top:20px"><h3>${esc(o.name)}</h3>
      <h3>Contacts</h3>${tbl([["Tier", (c) => pill("t-" + c.tier, c.tier)], ["Method", (c) => esc(c.method)], ["Value", (c) => `<span style="word-break:break-all">${esc(c.value || "")}</span>`], ["Evidence", (c) => c.evidence_url ? `<a href="${esc(c.evidence_url)}" target="_blank" rel="noopener">source</a>` : ""], ["Notes", (c) => `<span style="font-size:.78rem">${esc(c.notes || "")}</span>`]], o.contacts)}
      <h3>Sourced personalisation facts</h3><ul>${o.facts.map((f) => `<li>${esc(f.fact)} <a href="${esc(f.source_url)}" target="_blank" rel="noopener">source</a></li>`).join("") || "<li class='muted'>None verified, so the draft will not mention one.</li>"}</ul>
      <div class="two form" style="margin:12px 0"><label>Founder name for drafts<input id="fname" placeholder="Founder name"></label></div>
      <button class="btn accent" id="draft">Draft initial enquiry</button>
      <h3>Messages</h3>${o.messages.map((m) => `<div style="margin:10px 0"><div class="mono">#${m.id} · step ${m.sequence_step} · ${esc(m.status)}</div><div><b>${esc(m.subject)}</b></div><pre class="draft">${esc(m.body)}</pre>
        ${m.status === "DRAFT" ? `<button class="btn" data-approve="${m.id}">Founder approve</button>` : ""}</div>`).join("") || "<p class='muted'>No messages.</p>"}<div class="out"></div></div>`;
    $("#draft").addEventListener("click", async () => {
      try { await api(`/admin/crm/${encodeURIComponent(oid)}/draft`, { method: "POST", body: { founder_name: $("#fname").value || undefined } }); await orgDetail(oid); }
      catch (e) { $(".out", box).innerHTML = `<div class="msg err">${esc(e.message)}</div>`; }
    });
    box.querySelectorAll("[data-approve]").forEach((b) => b.addEventListener("click", async () => {
      const name = $("#fname").value;
      try { const r = await api(`/admin/outreach/${b.dataset.approve}/approve`, { method: "POST", body: { founder_name: name } }); $(".out", box).innerHTML = `<div class="msg ok">${esc(r.note)}</div>`; await orgDetail(oid); }
      catch (e) { $(".out", box).innerHTML = `<div class="msg err">${esc(e.message)}</div>`; }
    }));
    box.scrollIntoView({ behavior: "smooth" });
  }

  refreshMe().then(render);
})();
