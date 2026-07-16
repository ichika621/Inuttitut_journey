/* Inuttut Journey — a visual-novel RPG for learning Inuttut (Labrador Inuit).
 *
 * You play the first-person protagonist of a Labrador folktale: illustrated
 * story beats, visual-novel CONVERSATIONS with characters (whose expression
 * changes per line) where Inuttut words are taught, and turn-based word BATTLES
 * that test them — all with a fully-synthesised soundtrack (js/audio.js).
 *
 * ALL vocabulary is from data/dictionary.json (the Labrador Virtual Museum
 * English-Inuttut Dictionary). data/story.json is the scene graph; every Inuttut
 * word it uses is validated against the dictionary and embedded in `words`.
 */
(function () {
  "use strict";

  var DICT = [], DICT_BY_ID = {}, STORY = null, META = {}, ACTS = [], WORDS = {}, CHARS = {};
  var NOUNS = [];   // nouns-only pool for battle distractors (data/nouns.json)
  var A = (window.Game && window.Game.audio) || { init: function () {}, setEnabled: function () {}, isEnabled: function () { return false; }, bgm: function () {}, amb: function () {}, sfx: function () {} };
  var app = document.getElementById("app");
  var STORE_KEY = "inuttut-vn-v1";
  var XP_CORRECT = 6, XP_WORD = 4, XP_BATTLE = 60, XP_ACT = 50, XP_LEVEL = 120;
  var state = load();
  var audioReady = false, curBgm = null, curAmb = null;

  /* ---------- data ---------- */
  function boot() {
    Promise.all([grab("data/dictionary.json", "DICTIONARY"), grab("data/story.json", "STORY"),
                 grab("data/nouns.json", "NOUNS")])
      .then(function (r) {
        DICT = r[0] || []; STORY = r[1] || {}; NOUNS = r[2] || [];
        META = STORY.meta || {}; ACTS = STORY.acts || []; WORDS = STORY.words || {}; CHARS = STORY.characters || {};
        DICT.forEach(function (e) { DICT_BY_ID[e.id] = e; });
        if (!NOUNS.length) NOUNS = DICT.filter(function (e) { return e.pos === "n."; }); // fallback
        wireChrome(); routeFromHash();
      });
  }
  function grab(url, g) { return fetch(url, { cache: "no-store" }).then(function (r) { if (!r.ok) throw 0; return r.json(); }).catch(function () { return window[g]; }); }

  /* ---------- persistence ---------- */
  function fresh() { return { level: 1, xp: 0, unlocked: 1, scene: {}, actDone: {}, guide: {}, cards: [], srs: [], answered: 0, correct: 0, battles: 0, sound: true }; }
  function load() { try { var s = JSON.parse(localStorage.getItem(STORE_KEY)); if (s && s.guide) return Object.assign(fresh(), s); } catch (e) {} return fresh(); }
  function save() { try { localStorage.setItem(STORE_KEY, JSON.stringify(state)); } catch (e) {} }

  /* ---------- helpers ---------- */
  function el(t, c, h) { var n = document.createElement(t); if (c) n.className = c; if (h != null) n.innerHTML = h; return n; }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function shuffle(a) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
  function word(id) { return WORDS[id] || DICT_BY_ID[id]; }
  function primary(r) { return r.inuttut[0]; }
  function hasIcon(r) { return r && r.image && r.image.indexOf("_placeholder") < 0; }
  function actById(id) { return ACTS.filter(function (a) { return a.id === id; })[0]; }
  function actIndex(id) { for (var i = 0; i < ACTS.length; i++) if (ACTS[i].id === id) return i; return -1; }
  function portraitPath(who, expr) { var c = CHARS[who]; return c ? c.dir + "/" + expr + ".svg" : ""; }

  var toastTimer;
  function toast(m) { var t = document.getElementById("toast"); if (!t) { t = el("div", "toast"); t.id = "toast"; document.body.appendChild(t); } t.textContent = m; t.classList.add("show"); clearTimeout(toastTimer); toastTimer = setTimeout(function () { t.classList.remove("show"); }, 2000); }

  /* ---------- audio ---------- */
  function ensureAudio() { if (!audioReady) { A.init(); A.setEnabled(state.sound); audioReady = true; if (curBgm) A.bgm(curBgm); if (curAmb) A.amb(curAmb); } }
  function setScnAudio(bgm, amb) { curBgm = bgm || null; curAmb = amb || null; if (audioReady) { A.bgm(curBgm); A.amb(curAmb); } }
  function sfx(n) { if (n) A.sfx(n); }

  /* ---------- xp / srs ---------- */
  function addXp(n) { state.xp += n; var lv = Math.floor(state.xp / XP_LEVEL) + 1; if (lv > state.level) { state.level = lv; sfx("levelup"); toast("Level up! You are level " + lv + "."); } save(); refreshHud(); }
  function recordAnswer(id, ok) { var g = state.guide[id] || (state.guide[id] = { seen: 0, correct: 0, wrong: 0 }); g.seen++; state.answered++; if (ok) { g.correct++; state.correct++; addXp(XP_CORRECT); demote(id); } else { g.wrong++; promote(id); } save(); }
  function fileWord(id) { if (!state.guide[id]) { state.guide[id] = { seen: 0, correct: 0, wrong: 0 }; addXp(XP_WORD); sfx("word_learned"); save(); } }
  function promote(id) { var f = state.srs.filter(function (x) { return x.id === id; })[0]; if (f) f.due = state.answered + 2; else state.srs.push({ id: id, due: state.answered + 2 }); }
  function demote(id) { state.srs = state.srs.filter(function (x) { return x.id !== id; }); }
  function dueReview(ex) { return state.srs.filter(function (x) { return x.due <= state.answered && ex.indexOf(x.id) < 0; }).map(function (x) { return x.id; }); }

  // Distractors are drawn from the NOUNS-ONLY pool, so every wrong option is also
  // a real dictionary noun (never a verb/adjective/phrase).
  function distractors(target, n, iconOnly) {
    var used = {}; used[primary(target).toLowerCase()] = 1; var pools = [];
    if (iconOnly) { pools.push(NOUNS.filter(function (e) { return e.theme === target.theme && e.id !== target.id && hasIcon(e); })); pools.push(NOUNS.filter(function (e) { return e.id !== target.id && hasIcon(e); })); }
    pools.push(NOUNS.filter(function (e) { return e.theme === target.theme && e.id !== target.id && e.inuttut.length && !e.uncertain; }));
    pools.push(NOUNS.filter(function (e) { return e.id !== target.id && e.inuttut.length; }));
    var out = [];
    for (var p = 0; p < pools.length && out.length < n; p++) { var pool = shuffle(pools[p]); for (var i = 0; i < pool.length && out.length < n; i++) { var k = primary(pool[i]).toLowerCase(); if (used[k]) continue; used[k] = 1; out.push(pool[i]); } }
    return out;
  }

  /* ---------- chrome / nav ---------- */
  function wireChrome() {
    document.getElementById("homeBtn").onclick = function () { go("map"); };
    Array.prototype.forEach.call(document.querySelectorAll("[data-nav]"), function (b) { b.onclick = function () { ensureAudio(); sfx("menu_click"); go(b.getAttribute("data-nav")); }; });
    document.addEventListener("click", function () { ensureAudio(); }, { once: false });
    window.addEventListener("hashchange", routeFromHash);
    refreshHud();
  }
  function go(r) { location.hash = "#/" + r; }
  function routeFromHash() {
    var h = (location.hash || "#/map").replace(/^#\//, ""), parts = h.split("/");
    setNavActive(parts[0]); window.scrollTo(0, 0); app.focus({ preventScroll: true });
    if (parts[0] === "play" && parts[1]) return renderPlay(parts[1]);
    if (parts[0] === "guide") return renderGuide();
    if (parts[0] === "cards") return renderCards();
    if (parts[0] === "about") return renderAbout();
    setScnAudio(null, null); return renderMap();
  }
  function setNavActive(route) {
    var map = { play: "map", map: "map", guide: "guide", cards: "cards", about: "about" };
    Array.prototype.forEach.call(document.querySelectorAll("[data-nav]"), function (b) { b.setAttribute("aria-current", map[route] === b.getAttribute("data-nav") ? "true" : "false"); });
  }
  function refreshHud() {
    var hud = document.getElementById("hud"); if (!hud) return;
    var into = state.xp % XP_LEVEL, pct = Math.round(into / XP_LEVEL * 100);
    hud.innerHTML = "";
    var lv = el("span", "lvl", "Lv " + state.level);
    var bar = el("span", "xpbar"); bar.appendChild(el("span")).style.width = pct + "%";
    var snd = el("button", "sound-btn", state.sound ? "🔊" : "🔇");
    snd.title = "Sound on/off"; snd.setAttribute("aria-label", "Toggle sound");
    snd.onclick = function () { ensureAudio(); state.sound = !state.sound; A.setEnabled(state.sound); save(); snd.textContent = state.sound ? "🔊" : "🔇"; sfx("menu_click"); };
    hud.appendChild(lv); hud.appendChild(bar); hud.appendChild(snd);
  }

  /* ==================================================================== */
  /*  MAP                                                                 */
  /* ==================================================================== */
  function renderMap() {
    app.innerHTML = "";
    var hero = el("section", "hero-map"); hero.style.backgroundImage = "url('assets/bg/sky_road_stars.svg')";
    var ov = el("div", "hero-map-in");
    ov.appendChild(el("h1", null, "Inuttut Journey"));
    ov.appendChild(el("p", "lede", "Walk a Labrador Inuit folktale in first person. Talk with the people you meet in <strong>Inuttut</strong>, learn their words, and win word-battles to bring back the light. Every word is real — from the Labrador Virtual Museum dictionary."));
    var learned = Object.keys(state.guide).filter(function (id) { return state.guide[id].correct > 0; }).length;
    var sr = el("div", "stat-row");
    [[state.level, "level"], [learned, "words learned"], [state.cards.length, "culture cards"], [state.battles, "battles won"]].forEach(function (s) { var d = el("div", "stat"); d.appendChild(el("b", null, String(s[0]))); d.appendChild(el("span", null, s[1])); sr.appendChild(d); });
    ov.appendChild(sr); hero.appendChild(ov); app.appendChild(hero);

    var trail = el("div", "trail");
    ACTS.forEach(function (a, i) { trail.appendChild(actNode(a, i)); });
    app.appendChild(trail);
    var note = el("p", "muted tiny");
    note.innerHTML = "🔊 Music &amp; sound are fully synthesised (no recordings). No pronunciation audio is faked — recordings exist at the <a href='" + esc(META.sourceUrl || "#") + "' target='_blank' rel='noopener'>source museum site</a>. Art is original placeholder for cultural review (see About).";
    app.appendChild(note);
  }
  function actNode(a, i) {
    var unlocked = i < state.unlocked, done = !!state.actDone[a.id];
    var node = el("div", "trail-node" + (unlocked ? "" : " locked") + (done ? " done" : ""));
    node.appendChild(el("div", "trail-badge tier" + (i + 1), unlocked ? (done ? "✔" : (i + 1)) : "🔒"));
    var card = el("button", "trail-card");
    card.appendChild(el("span", "pill tier" + (i + 1), "Act " + (i + 1)));
    card.appendChild(el("h3", null, esc(a.title)));
    card.appendChild(el("p", "tale", "Tale: " + esc(a.tale)));
    var idx = state.scene[a.id] || 0, tot = a.scenes.length;
    var bar = el("div", "progress"); bar.appendChild(el("span")).style.width = Math.round((done ? tot : Math.min(idx, tot)) / tot * 100) + "%";
    card.appendChild(bar);
    card.appendChild(el("p", done ? "done" : "muted tiny", done ? "Complete — Culture Card earned" : unlocked ? ("Scene " + Math.min(idx + 1, tot) + " of " + tot) : "Locked"));
    if (unlocked) card.onclick = function () { ensureAudio(); sfx("menu_click"); location.hash = "#/play/" + a.id; };
    node.appendChild(card); return node;
  }

  /* ==================================================================== */
  /*  SCENE PLAYER (beats)                                                */
  /* ==================================================================== */
  function renderPlay(actId) {
    var a = actById(actId); if (!a) return renderMap();
    if (actIndex(actId) >= state.unlocked) { toast("That act is locked."); return renderMap(); }
    var idx = state.scene[actId] || 0;
    if (idx >= a.scenes.length) return renderActEnd(a);
    renderScene(a, idx);
  }
  function nextScene(a, idx) { var n = idx + 1; state.scene[a.id] = n; save(); if (n >= a.scenes.length) return renderActEnd(a); renderScene(a, n); }

  function renderScene(a, idx) {
    var sc = a.scenes[idx];
    ensureAudio(); setScnAudio(sc.bgm, sc.amb);
    app.innerHTML = "";
    var stage = el("section", "stage"); stage.style.backgroundImage = "url('assets/bg/" + sc.bg + ".svg')";
    var top = el("div", "stage-top");
    top.appendChild(el("div", "crumb", "<a href='#/map'>Map</a> · " + esc(a.title) + " · " + esc(sc.title)));
    top.appendChild(sceneDots(a, idx));
    stage.appendChild(top);
    var spriteLayer = el("div", "sprite-layer"); stage.appendChild(spriteLayer);
    var boxHolder = el("div", "box-holder"); stage.appendChild(boxHolder);
    app.appendChild(stage);

    var beats = sc.beats, bi = 0, lastWho = null, cast = [];
    // cast = up to 2 on-stage characters, most-recent (active speaker) last
    function stageCast(activeWho, expr) {
      var found = false;
      for (var i = 0; i < cast.length; i++) if (cast[i].who === activeWho) { cast[i].expr = expr; cast.splice(cast.length, 0, cast.splice(i, 1)[0]); found = true; break; }
      if (!found) cast.push({ who: activeWho, expr: expr });
      // keep the active plus at most one other distinct character
      while (cast.length > 2) cast.shift();
      spriteLayer.innerHTML = "";
      cast.forEach(function (c, i) {
        var active = i === cast.length - 1;
        var sp = el("div", "sprite " + (active ? "active" : "dimmed") + (cast.length > 1 ? (active ? " right" : " left") : " solo"));
        var img = el("img"); img.src = portraitPath(c.who, c.expr);
        img.alt = ((CHARS[c.who] || {}).name || "") + (active ? " (" + c.expr + ")" : "");
        sp.appendChild(img); spriteLayer.appendChild(sp);
      });
    }
    function step() {
      var beat = beats[bi];
      if (!beat) return nextScene(a, idx);
      if (beat.t === "narr") return doNarr(beat);
      if (beat.t === "line") return doLine(beat);
      if (beat.t === "choice") return doChoice(beat);
      if (beat.t === "battle") return doBattle(beat);
      bi++; step();
    }
    function advance() { bi++; step(); }

    function doNarr(beat) {
      sfx(beat.sfx);
      spriteLayer.classList.add("dim");
      boxHolder.innerHTML = "";
      var box = el("div", "narrate vn");
      box.appendChild(el("p", "inner", esc(beat.text.replace(/`([^`]+)`/g, "$1"))));
      var b = el("button", "btn small", "▸"); b.setAttribute("aria-label", "continue");
      b.onclick = function () { sfx("menu_click"); advance(); };
      box.appendChild(b); boxHolder.appendChild(box);
    }

    function doLine(beat) {
      spriteLayer.classList.remove("dim");
      var ch = CHARS[beat.who] || { name: "?" };
      // show the active speaker foregrounded; any other on-stage character dims
      stageCast(beat.who, beat.expr);
      lastWho = beat.who;
      // file taught words + chime (once each)
      (beat.words || []).forEach(function (id) { fileWord(id); });
      sfx(beat.sfx || "text_blip");
      boxHolder.innerHTML = "";
      var box = el("div", "vnbox");
      box.appendChild(el("div", "vn-name", esc(ch.name) + " <span class='vn-expr'>· " + esc(beat.expr) + "</span>"));
      box.appendChild(lineText(beat));
      if (beat.words && beat.words.length) box.appendChild(el("div", "vn-hint tiny", "Tap a glowing word to learn it — it's saved to your Field Guide."));
      var b = el("button", "btn small", "Next ›"); b.onclick = function () { sfx("menu_click"); advance(); };
      box.appendChild(b); boxHolder.appendChild(box);
    }

    function lineText(beat) {
      var p = el("p", "vn-line");
      var parts = beat.text.split(/(`[^`]+`)/);
      parts.forEach(function (seg) {
        if (/^`.*`$/.test(seg)) {
          var form = seg.slice(1, -1);
          var rec = (beat.words || []).map(word).filter(Boolean).filter(function (r) { return r.inuttut.indexOf(form) >= 0; })[0];
          var chip = el("button", "vn-chip", esc(form));
          if (rec) chip.onclick = function () { fileWord(rec.id); showWordPopup(rec); };
          p.appendChild(chip);
        } else if (seg) { p.appendChild(document.createTextNode(seg)); }
      });
      return p;
    }

    function doChoice(beat) {
      boxHolder.innerHTML = "";
      var box = el("div", "vnbox");
      if (lastWho) box.appendChild(el("div", "vn-name", esc((CHARS[lastWho] || {}).name || "")));
      var opts = el("div", "reply-opts");
      (beat.options || ["Continue."]).forEach(function (o) { var r = el("button", "reply", esc(o)); r.onclick = function () { sfx("menu_click"); advance(); }; opts.appendChild(r); });
      box.appendChild(opts); boxHolder.appendChild(box);
    }

    function doBattle(beat) {
      spriteLayer.innerHTML = ""; spriteLayer.classList.remove("dim");
      runBattle(stage, spriteLayer, boxHolder, beat, function () { advance(); });
    }

    step();
  }

  function sceneDots(a, idx) {
    var d = el("div", "scene-dots");
    a.scenes.forEach(function (s, i) { var hasBattle = s.beats.some(function (b) { return b.t === "battle"; }); d.appendChild(el("i", (hasBattle ? "t-battle " : "") + (i < idx ? "on " : "") + (i === idx ? "cur" : ""))); });
    return d;
  }

  function showWordPopup(rec) {
    if (!rec) return; sfx("menu_click");
    var back = el("div", "modal-back"); var m = el("div", "modal");
    if (hasIcon(rec)) { var im = el("img", "modal-img"); im.src = rec.image; im.alt = ""; m.appendChild(im); }
    m.appendChild(el("div", "modal-inuttut", esc(primary(rec))));
    m.appendChild(el("div", "modal-en", esc(rec.english)));
    if (rec.inuttut.length > 1) m.appendChild(el("div", "muted tiny", "also: " + esc(rec.inuttut.slice(1).join(", "))));
    var meta = el("div", "modal-meta");
    if (rec.pos) meta.appendChild(el("span", "pill", rec.pos === "v." ? "verb" : "noun"));
    meta.appendChild(el("span", "pill theme", esc((rec.theme || "").replace("_", " / "))));
    if (rec.uncertain) meta.appendChild(el("span", "pill unc", "source unsure ?"));
    m.appendChild(meta);
    m.appendChild(el("div", "muted tiny", "Dictionary entry #" + rec.id + " · spelling exactly as in the source"));
    var cl = el("button", "btn small", "Close"); cl.onclick = function () { back.remove(); };
    m.appendChild(cl); back.appendChild(m);
    back.onclick = function (e) { if (e.target === back) back.remove(); };
    document.body.appendChild(back);
  }

  /* ==================================================================== */
  /*  BATTLE                                                              */
  /* ==================================================================== */
  function runBattle(stage, spriteLayer, boxHolder, beat, onWin) {
    setScnAudio("battle", curAmb);
    var stages = beat.stages || [beat.enemyPortrait || "shadow"];
    var maxE = beat.enemyHp, maxP = beat.playerHp, st = { eHp: maxE, pHp: maxP, round: 0 };

    // enemy panel in sprite layer
    spriteLayer.innerHTML = "";
    var epanel = el("div", "combatant enemy");
    epanel.appendChild(el("div", "cbt-name", esc(beat.enemy)));
    var ehp = hpBar("enemy"); epanel.appendChild(ehp.wrap);
    var esprite = el("div", "sprite enemy-sprite"); var eimg = el("img"); eimg.alt = beat.enemy; esprite.appendChild(eimg); epanel.appendChild(esprite);
    spriteLayer.appendChild(epanel);

    boxHolder.innerHTML = "";
    var ppanel = el("div", "combatant player"); ppanel.appendChild(el("div", "cbt-name", "You"));
    var php = hpBar("player"); ppanel.appendChild(php.wrap); boxHolder.appendChild(ppanel);
    var arena = el("div", "arena"); boxHolder.appendChild(arena);

    function stageSprite() {
      var frac = Math.max(0, st.eHp) / maxE; // 1..0
      var i = Math.min(stages.length - 1, Math.floor((1 - frac) * stages.length));
      if (frac <= 0) i = stages.length - 1;
      eimg.src = "assets/chars/" + stages[i] + ".svg";
    }
    function setHp() { ehp.set(st.eHp / maxE); ehp.label(Math.max(0, st.eHp) + "/" + maxE); php.set(st.pHp / maxP); php.label(Math.max(0, st.pHp) + "/" + maxP); stageSprite(); }
    stageSprite(); setHp();

    var intro = el("div", "battle-intro"); intro.appendChild(el("p", null, esc(beat.intro)));
    var go = el("button", "btn", "Fight ›"); go.onclick = function () { sfx("menu_click"); turn(); }; intro.appendChild(go); arena.appendChild(intro);

    var typeOrder = beat.types.slice();
    function nextType() { return typeOrder[(st.round - 1) % typeOrder.length]; }
    function poolRecs() { var ids = beat.pool.slice(); var rev = dueReview(ids).slice(0, 1); return shuffle(ids.concat(rev)).map(word).filter(Boolean); }

    function hit(target, dmg, w) {
      if (target === "enemy") { st.eHp -= dmg; flash(esprite, "hit-enemy"); floatNum(esprite, "-" + dmg, "dmg"); sfx("enemy_hit"); if (w) toast("You wield " + w + "!"); }
      else { st.pHp -= dmg; flash(stage, "shake"); floatNum(esprite, beat.enemy.split(" ")[0] + "!", "enemyhit"); }
      setHp();
    }
    function turn() {
      arena.innerHTML = "";
      if (st.eHp <= 0) return victory();
      if (st.pHp <= 0) return defeat();
      st.round++;
      var t = nextType();
      arena.appendChild(el("div", "turn-head", "Turn " + st.round + " · " + ({ picmc: "Pick the picture", mc: "Choose the word", match: "Match the pairs", order: "Put the nouns in order" }[t] || "Choose the word")));
      if (t === "order" && beat.sequences && beat.sequences.length) return orderTurn();
      if (t === "match") return matchTurn();
      if (t === "picmc") return mcTurn(true);
      return mcTurn(false);
    }

    function finishBtn(label, fn) { var b = el("button", "btn small", label || "Continue ›"); b.onclick = function () { sfx("menu_click"); fn(); }; return b; }

    function mcTurn(picture) {
      var recs = poolRecs(), target = recs[0];
      if (picture && !hasIcon(target)) picture = false;
      var others = distractors(target, 3, picture);
      if (picture && others.filter(hasIcon).length < 3) picture = false;
      var opts = shuffle([target].concat(others));
      var q = el("div", "q"); var fb = el("div", "feedback");
      if (picture) {
        q.appendChild(el("div", "q-prompt", "Which picture is “<span class='inuttut'>" + esc(primary(target)) + "</span>”?"));
        var grid = el("div", "opt-pics");
        opts.forEach(function (o) { var b = el("button", "opt-pic"); var im = el("img"); im.src = o.image; im.alt = o.english; b.appendChild(im); b.appendChild(el("span", "opt-cap", esc(o.english))); b.onclick = function () { pick(o.id === target.id, b, grid, target, opts); }; grid.appendChild(b); });
        q.appendChild(grid);
      } else {
        var toI = Math.random() < 0.5;
        q.appendChild(el("div", "q-prompt", toI ? "Say “<em>" + esc(target.english) + "</em>” in Inuttut" : "What does “<span class='inuttut'>" + esc(primary(target)) + "</span>” mean?"));
        if (hasIcon(target) && !toI) { var pim = el("img", "q-hint"); pim.src = target.image; pim.alt = ""; q.appendChild(pim); }
        var box = el("div", "opt-text");
        opts.forEach(function (o) { var b = el("button", "opt" + (toI ? " inuttut" : ""), esc(toI ? primary(o) : o.english)); b.onclick = function () { pick(o.id === target.id, b, box, target, opts, toI); }; box.appendChild(b); });
        q.appendChild(box);
      }
      q.appendChild(fb); arena.appendChild(q); q._fb = fb; arena._q = q;
    }
    function pick(ok, btn, box, target, opts, toI) {
      Array.prototype.forEach.call(box.children, function (b) { b.disabled = true; });
      recordAnswer(target.id, ok); btn.classList.add(ok ? "correct" : "wrong");
      if (!ok) Array.prototype.forEach.call(box.children, function (b, i) { if (opts[i] && opts[i].id === target.id) b.classList.add("correct"); });
      var fb = arena._q._fb;
      if (ok) { fb.className = "feedback ok"; fb.textContent = "Correct!"; sfx("correct"); hit("enemy", Math.ceil(maxE / beat.rounds), primary(target)); }
      else { fb.className = "feedback no"; fb.textContent = "“" + primary(target) + "” = " + target.english + "."; sfx("wrong"); hit("player", Math.ceil(maxP / (beat.rounds + 2))); }
      arena._q.appendChild(finishBtn("Continue ›", turn));
    }

    function matchTurn() {
      var recs = shuffle(poolRecs()).slice(0, 4);
      var q = el("div", "q"); q.appendChild(el("div", "q-prompt", "Match each word to its meaning"));
      var grid = el("div", "match-grid"), left = el("div", "match-col"), right = el("div", "match-col");
      grid.appendChild(left); grid.appendChild(right); q.appendChild(grid);
      var fb = el("div", "feedback"); q.appendChild(fb); arena.appendChild(q);
      shuffle(recs).forEach(function (r) { var m = el("button", "match inuttut", esc(primary(r))); m.dataset.id = r.id; m.dataset.side = "i"; left.appendChild(m); });
      shuffle(recs).forEach(function (r) { var m = el("button", "match"); m.dataset.id = r.id; m.dataset.side = "e"; if (hasIcon(r)) { var im = el("img", "match-ic"); im.src = r.image; im.alt = ""; m.appendChild(im); } m.appendChild(el("span", null, esc(r.english))); right.appendChild(m); });
      var sel = null, remaining = recs.length, took = false;
      grid.addEventListener("click", function (e) {
        var m = e.target.closest(".match"); if (!m || m.classList.contains("matched")) return;
        if (!sel) { clear(); sel = m; m.classList.add("sel"); return; }
        if (sel === m) { m.classList.remove("sel"); sel = null; return; }
        if (sel.dataset.side === m.dataset.side) { clear(); sel = m; m.classList.add("sel"); return; }
        var ok = sel.dataset.id === m.dataset.id; recordAnswer(Number(m.dataset.id), ok);
        if (ok) { sel.classList.add("matched"); m.classList.add("matched"); sel.classList.remove("sel"); sel = null; remaining--; fb.className = "feedback ok"; fb.textContent = "Matched!"; sfx("correct"); hit("enemy", Math.max(1, Math.round(maxE / beat.rounds / 2))); if (remaining === 0) { fb.textContent = "All matched!"; q.appendChild(finishBtn("Continue ›", turn)); } }
        else { var aa = sel, bb = m; aa.classList.add("err"); bb.classList.add("err"); fb.className = "feedback no"; fb.textContent = "Not a pair."; sfx("wrong"); if (!took) { hit("player", Math.ceil(maxP / (beat.rounds + 2))); took = true; } setTimeout(function () { aa.classList.remove("err", "sel"); bb.classList.remove("err"); }, 480); sel = null; if (st.pHp <= 0) setTimeout(defeat, 520); }
      });
      function clear() { Array.prototype.forEach.call(grid.querySelectorAll(".sel"), function (x) { x.classList.remove("sel"); }); }
    }

    // "order" = tap the Inuttut NOUN labels in the order the English names them.
    // This is a recall/sequence exercise on independent noun labels — NOT a
    // constructed sentence and no grammar is asserted.
    function orderTurn() {
      var s = shuffle(beat.sequences.slice())[0], recs = s.tokenIds.map(word), target = recs.map(primary);
      var q = el("div", "q"); q.appendChild(el("div", "q-prompt", "In order: <em>" + esc(s.gloss) + "</em>"));
      q.appendChild(el("div", "muted tiny", "Tap the Inuttut nouns in the order named above. Each is a real dictionary noun."));
      var ans = el("div", "tokens"), tray = el("div", "tray"), built = [];
      shuffle(recs).forEach(function (r) { var t = el("button", "token", esc(primary(r))); t.onclick = function () { t.remove(); built.push(primary(r)); var pl = el("button", "token", esc(primary(r))); pl.onclick = function () { pl.remove(); built.splice(built.indexOf(primary(r)), 1); tray.appendChild(t); check(); }; ans.appendChild(pl); check(); }; tray.appendChild(t); });
      q.appendChild(ans); q.appendChild(tray);
      var fb = el("div", "feedback"); q.appendChild(fb);
      q.appendChild(el("div", "review-flag tiny", "ⓘ " + (s.note || "A sequence of separate noun labels — not a sentence.")));
      arena.appendChild(q);
      function check() { if (built.length < target.length) { fb.textContent = ""; return; } var ok = built.join(" ") === target.join(" "); recs.forEach(function (r) { recordAnswer(r.id, ok); }); fb.className = "feedback " + (ok ? "ok" : "no"); if (ok) { fb.textContent = "That's the order."; sfx("correct"); hit("enemy", Math.ceil(maxE / beat.rounds) + 1, s.gloss); q.appendChild(finishBtn("Continue ›", turn)); } else { fb.textContent = "Not that order — tap a placed noun to send it back."; sfx("wrong"); hit("player", Math.ceil(maxP / (beat.rounds + 2))); if (st.pHp <= 0) setTimeout(defeat, 400); } }
    }

    function victory() {
      state.battles++; addXp(XP_BATTLE); save(); flash(esprite, "faint"); sfx("enemy_defeated"); setTimeout(function () { sfx("victory_jingle"); }, 400); setScnAudio(null, curAmb);
      arena.innerHTML = ""; var v = el("div", "battle-result win");
      v.appendChild(el("h3", null, "Victory! ✦  +" + XP_BATTLE + " XP"));
      v.appendChild(el("p", null, esc(beat.victory)));
      v.appendChild(finishBtn("Continue ›", function () { setScnAudio(curBgm, curAmb); onWin(); })); arena.appendChild(v);
    }
    function defeat() {
      arena.innerHTML = ""; var v = el("div", "battle-result lose");
      v.appendChild(el("h3", null, "You are overwhelmed…"));
      v.appendChild(el("p", null, "Catch your breath — the words reshuffle and you try again. (No progress lost.)"));
      v.appendChild(finishBtn("Try again ›", function () { st.eHp = maxE; st.pHp = maxP; st.round = 0; setHp(); arena.innerHTML = ""; arena.appendChild(intro); })); arena.appendChild(v);
    }
  }

  function hpBar(kind) {
    var wrap = el("div", "hp " + kind), fill = el("span", "hp-fill"), lab = el("span", "hp-label");
    wrap.appendChild(fill); wrap.appendChild(lab);
    return { wrap: wrap, set: function (r) { fill.style.width = Math.max(0, Math.min(1, r)) * 100 + "%"; fill.className = "hp-fill" + (r < 0.34 ? " low" : r < 0.67 ? " mid" : ""); }, label: function (t) { lab.textContent = t; } };
  }
  function flash(n, c) { if (!n) return; n.classList.remove(c); void n.offsetWidth; n.classList.add(c); setTimeout(function () { n.classList.remove(c); }, 620); }
  function floatNum(n, t, c) { if (!n) return; var f = el("div", "floatnum " + (c || ""), esc(t)); n.appendChild(f); setTimeout(function () { f.remove(); }, 900); }

  /* ==================================================================== */
  /*  ACT END + CULTURE CARD                                              */
  /* ==================================================================== */
  function renderActEnd(a) {
    if (state.cards.indexOf(a.id) < 0) { state.cards.push(a.id); addXp(XP_ACT); }
    state.actDone[a.id] = true;
    var i = actIndex(a.id); if (i + 1 >= state.unlocked && i + 1 < ACTS.length) state.unlocked = i + 2;
    save(); setScnAudio("reprise", null);
    app.innerHTML = "";
    app.appendChild(el("div", "crumb", "<a href='#/map'>Map</a> · " + esc(a.title) + " · complete"));
    app.appendChild(el("h2", null, "Act complete ✦"));
    app.appendChild(el("p", "muted", "A Culture Card joins your Field Guide."));
    app.appendChild(cultureCardEl(a));
    var row = el("div", "row"); row.style.marginTop = "18px";
    var next = ACTS[i + 1];
    if (next) { var nb = el("button", "btn", "Journey on: " + next.title + " ›"); nb.onclick = function () { sfx("menu_click"); location.hash = "#/play/" + next.id; }; row.appendChild(nb); }
    else row.appendChild(el("p", "done", "🎉 You brought back the morning. Inuttut Journey complete."));
    var hb = el("button", "btn secondary", "Return to map"); hb.onclick = function () { go("map"); }; row.appendChild(hb);
    app.appendChild(row);
  }
  function cultureCardEl(a) {
    var c = a.culture, card = el("section", "culture");
    card.appendChild(el("span", "pill tier" + (actIndex(a.id) + 1), "Culture Card"));
    card.appendChild(el("h3", null, esc(c.title)));
    card.appendChild(el("p", null, esc(c.body)));
    if (c.source) card.appendChild(el("p", "source-note", "Tale: <strong>" + esc(a.tale) + "</strong> · Source: " + esc(c.source) + (c.community ? " · " + esc(c.community) : "")));
    if (c.reviewNote) card.appendChild(el("div", "review-flag", "⚠ " + esc(c.reviewNote)));
    return card;
  }

  /* ==================================================================== */
  /*  FIELD GUIDE                                                         */
  /* ==================================================================== */
  function renderGuide() {
    setScnAudio("home", null);
    app.innerHTML = ""; app.appendChild(el("h2", null, "Field Guide"));
    var ids = Object.keys(state.guide).map(Number).filter(function (id) { return word(id); });
    app.appendChild(el("p", "muted", "Your illustrated picture-dictionary — every Inuttut word you have met. <strong>" + ids.length + "</strong> collected."));
    if (!ids.length) { app.appendChild(el("div", "empty", "No words yet — begin Act 1 to start collecting.")); return; }
    var tools = el("div", "guide-tools"); var search = el("input", "search"); search.type = "search"; search.placeholder = "Search English or Inuttut…"; tools.appendChild(search); app.appendChild(tools);
    var grid = el("div", "pic-grid"); app.appendChild(grid);
    function draw(qs) {
      grid.innerHTML = ""; qs = (qs || "").trim().toLowerCase();
      var recs = ids.map(word).sort(function (x, y) { return x.english.localeCompare(y.english); }), shown = 0;
      recs.forEach(function (r) { var hay = (r.english + " " + r.inuttut.join(" ")).toLowerCase(); if (qs && hay.indexOf(qs) < 0) return; shown++;
        var g = state.guide[r.id], mastered = g && g.correct > 0 && g.wrong <= g.correct;
        var card = el("button", "pic-card" + (mastered ? " mastered" : "")); var im = el("img", "pic-ic"); im.src = r.image; im.alt = ""; card.appendChild(im);
        card.appendChild(el("div", "pic-inuttut", esc(primary(r)))); card.appendChild(el("div", "pic-en", esc(r.english)));
        card.appendChild(el("div", "pic-meta tiny", (mastered ? "✔ learned · " : "seen " + g.seen + "× · ") + "#" + r.id));
        card.onclick = function () { showWordPopup(r); }; grid.appendChild(card); });
      if (!shown) grid.appendChild(el("div", "empty", "No matches."));
    }
    search.oninput = function () { draw(search.value); }; draw("");
  }

  /* ==================================================================== */
  /*  CULTURE CARDS + ABOUT                                               */
  /* ==================================================================== */
  function renderCards() {
    setScnAudio("home", null);
    app.innerHTML = ""; app.appendChild(el("h2", null, "Culture Cards"));
    if (!state.cards.length) { app.appendChild(el("div", "empty", "Finish an act to earn its Culture Card.")); return; }
    app.appendChild(el("p", "muted", "Earned as you complete acts."));
    state.cards.forEach(function (id) { var a = actById(id); if (a) { var w = el("div"); w.style.marginBottom = "16px"; w.appendChild(cultureCardEl(a)); app.appendChild(w); } });
  }
  function renderAbout() {
    setScnAudio("home", null);
    app.innerHTML = "";
    var c = el("section", "card");
    c.appendChild(el("h2", null, "About Inuttut Journey"));
    c.appendChild(el("p", null, "A first-person visual-novel RPG for learning <strong>Inuttut</strong> (Labrador Inuit / Nunatsiavut). You live a folktale, talk with characters to learn words, and win word-battles to advance."));
    c.appendChild(el("h3", null, "Where the words come from"));
    c.appendChild(el("p", null, "Every word is extracted from the <a href='" + esc(META.sourceUrl || "#") + "' target='_blank' rel='noopener'>Labrador Virtual Museum English-Inuttut Dictionary</a> (" + (META.totalDictionaryEntries || DICT.length) + " entries). This is Inuttut — <em>not</em> Inuktitut; spelling follows the dictionary exactly, including mid-word capital <span class='kbd'>K</span> and circumflex vowels. All 30 story words were validated against the dictionary before use."));
    c.appendChild(el("h3", null, "Sound"));
    c.appendChild(el("p", null, esc(META.audioNote || "All music and sound are synthesised at runtime; no recordings.")));
    c.appendChild(el("h3", null, "Art"));
    c.appendChild(el("p", null, esc(META.artNote || "Original placeholder illustration; a swappable asset layer for real, ideally Inuit-made, artwork.")));
    c.appendChild(el("h3", null, "The tales"));
    var ul = el("ul", "list-reset");
    ACTS.forEach(function (a) { var li = el("li"); li.style.marginBottom = "10px"; li.innerHTML = "<strong>" + esc(a.title) + "</strong> — " + esc(a.tale) + "<br><span class='muted tiny'>" + esc((a.culture && a.culture.source) || "") + ((a.culture && a.culture.community) ? " · " + esc(a.culture.community) : "") + "</span>"; ul.appendChild(li); });
    c.appendChild(ul);
    c.appendChild(el("h3", null, "Cultural care"));
    c.appendChild(el("div", "review-flag", "⚠ " + esc(META.culturalCaveat || "Review the tales, art, and audio with the Nunatsiavut Government / Torngâsok Cultural Centre before publishing.")));
    app.appendChild(c);
    var r = el("section", "card");
    r.appendChild(el("h3", null, "Progress"));
    r.appendChild(el("p", "muted", "Level " + state.level + " · " + state.xp + " XP · answered " + state.answered + " (" + state.correct + " correct). Saved in this browser only."));
    var rb = el("button", "btn secondary small", "Reset all progress");
    rb.onclick = function () { if (confirm("Erase all progress and start over?")) { state = fresh(); save(); refreshHud(); go("map"); } };
    r.appendChild(rb); app.appendChild(r);
  }

  boot();
})();
