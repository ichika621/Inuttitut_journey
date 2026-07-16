/* Inuttut Journey — procedural audio engine.
 *
 * ALL music, ambience, and sound effects are SYNTHESISED at runtime with the
 * Web Audio API — there are no audio files and nothing is sampled or recorded.
 * That makes the whole soundtrack royalty-free and self-contained (works from
 * file://), and guarantees NO sacred or ceremonial recordings are used
 * (a cultural-care requirement). See docs/audio-credits.md.
 *
 * Public API (window.Game.audio):
 *   init()                 create the AudioContext on a user gesture
 *   setEnabled(bool)       master mute/unmute (persisted by the app)
 *   isEnabled()            -> bool
 *   bgm(name)              crossfade to a looping music track (or null to stop)
 *   amb(name)              set the looping ambient bed (or null)
 *   sfx(name)              fire a one-shot sound effect
 */
(function () {
  "use strict";
  var AC = null, master = null, musicGain = null, ambGain = null, sfxGain = null;
  var enabled = true, started = false;
  var curBgm = null, bgmVoice = null, curAmb = null, ambVoice = null;
  var scheduler = null;

  function init() {
    if (AC) { if (AC.state === "suspended") AC.resume(); return; }
    var Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return;
    AC = new Ctx();
    master = AC.createGain(); master.gain.value = enabled ? 0.9 : 0; master.connect(AC.destination);
    musicGain = AC.createGain(); musicGain.gain.value = 0.42; musicGain.connect(master);
    ambGain = AC.createGain(); ambGain.gain.value = 0.30; ambGain.connect(master);
    sfxGain = AC.createGain(); sfxGain.gain.value = 0.75; sfxGain.connect(master);
    started = true;
    if (curBgm) startBgm(curBgm);
    if (curAmb) startAmb(curAmb);
    runScheduler();
  }
  function now() { return AC ? AC.currentTime : 0; }
  function setEnabled(v) {
    enabled = !!v;
    if (master) master.gain.setTargetAtTime(enabled ? 0.9 : 0, now(), 0.05);
  }
  function isEnabled() { return enabled; }

  /* ---------- low-level voices ---------- */
  function noiseBuffer(sec) {
    var n = Math.floor(AC.sampleRate * sec), b = AC.createBuffer(1, n, AC.sampleRate), d = b.getChannelData(0);
    for (var i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
    return b;
  }
  function env(g, t, a, d, peak, sus) {
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(peak, t + a);
    g.gain.exponentialRampToValueAtTime(Math.max(0.0001, sus == null ? peak * 0.6 : sus), t + a + d);
  }
  function tone(freq, t, dur, type, gainVal, dest) {
    var o = AC.createOscillator(), g = AC.createGain();
    o.type = type || "sine"; o.frequency.setValueAtTime(freq, t);
    o.connect(g); g.connect(dest || musicGain);
    env(g, t, 0.02, dur, gainVal || 0.2, 0.0001);
    g.gain.setTargetAtTime(0.0001, t + dur * 0.7, dur * 0.25);
    o.start(t); o.stop(t + dur + 0.05);
    return o;
  }

  /* ---------- BGM: a lookahead note scheduler ---------- */
  // Each track: {tempo (beats/sec), scale [freqs], build(bar)->[{beat,freq,dur,type,gain}], drone}
  var A2 = 110, C3 = 130.81, D3 = 146.83, E3 = 164.81, F3 = 174.61, G3 = 196,
      A3 = 220, B3 = 246.94, C4 = 261.63, D4 = 293.66, E4 = 329.63, F4 = 349.23,
      G4 = 392, A4 = 440, C5 = 523.25, D5 = 587.33, E5 = 659.25;

  function arp(notes, dur, type, gain) { // helper: even arpeggio across a bar (4 beats)
    return notes.map(function (f, i) { return { beat: i * (4 / notes.length), freq: f, dur: dur, type: type, gain: gain }; });
  }

  var TRACKS = {
    home: { tempo: 1.6, drone: A2, dgain: 0.06,
      bars: [ arp([A3, C4, E4, C4], 0.9, "sine", 0.14),
              arp([G3, C4, E4, D4], 0.9, "sine", 0.14),
              arp([F3, A3, C4, A3], 0.9, "sine", 0.14),
              arp([E3, G3, C4, G3], 0.9, "sine", 0.14) ] },
    land: { tempo: 2.2, drone: D3, dgain: 0.05,
      bars: [ arp([D4, F4, A4, F4, D4, A4], 0.5, "triangle", 0.11),
              arp([C4, E4, G4, E4, C4, G4], 0.5, "triangle", 0.11),
              arp([D4, F4, A4, D5, A4, F4], 0.5, "triangle", 0.11),
              arp([E4, G4, B3, G4, E4, D4], 0.5, "triangle", 0.11) ] },
    sea: { tempo: 1.1, drone: A2, dgain: 0.09,
      bars: [ [{beat:0,freq:E3,dur:2.4,type:"sine",gain:0.13},{beat:2,freq:G3,dur:2.0,type:"sine",gain:0.11}],
              [{beat:0,freq:D3,dur:2.4,type:"sine",gain:0.13},{beat:2,freq:F3,dur:2.0,type:"sine",gain:0.11}],
              [{beat:0,freq:C3,dur:2.8,type:"sine",gain:0.13}],
              [{beat:0,freq:E3,dur:2.4,type:"sine",gain:0.13},{beat:2,freq:A3,dur:2.0,type:"sine",gain:0.11}] ] },
    legend: { tempo: 1.4, drone: C3, dgain: 0.07,
      bars: [ [{beat:0,freq:C4,dur:2.0,type:"sine",gain:0.12},{beat:0,freq:E4,dur:2.0,type:"sine",gain:0.09},{beat:2,freq:G4,dur:1.8,type:"sine",gain:0.10}],
              [{beat:0,freq:A3,dur:2.0,type:"sine",gain:0.12},{beat:0,freq:C4,dur:2.0,type:"sine",gain:0.09},{beat:2,freq:E4,dur:1.8,type:"sine",gain:0.10}],
              [{beat:0,freq:F3,dur:2.0,type:"sine",gain:0.12},{beat:0,freq:A3,dur:2.0,type:"sine",gain:0.09},{beat:2,freq:C5,dur:1.8,type:"sine",gain:0.10}],
              [{beat:0,freq:G3,dur:2.4,type:"sine",gain:0.12},{beat:0,freq:D4,dur:2.4,type:"sine",gain:0.09}] ] },
    battle: { tempo: 3.0, drone: A2, dgain: 0.08,
      bars: [ arp([A3, A3, E4, A3, C4, A3, E4, C4], 0.22, "sawtooth", 0.07),
              arp([G3, G3, D4, G3, B3, G3, D4, B3], 0.22, "sawtooth", 0.07),
              arp([F3, F3, C4, F3, A3, F3, C4, A3], 0.22, "sawtooth", 0.07),
              arp([E3, E3, B3, E3, G3, E3, B3, G3], 0.22, "sawtooth", 0.07) ] },
    reprise: { tempo: 1.6, drone: A2, dgain: 0.10,
      bars: [ [{beat:0,freq:A3,dur:1.4,type:"triangle",gain:0.15},{beat:0,freq:E4,dur:1.4,type:"sine",gain:0.10},{beat:2,freq:C5,dur:1.6,type:"sine",gain:0.12}],
              [{beat:0,freq:G3,dur:1.4,type:"triangle",gain:0.15},{beat:0,freq:D4,dur:1.4,type:"sine",gain:0.10},{beat:2,freq:B3,dur:1.6,type:"sine",gain:0.12}],
              [{beat:0,freq:F3,dur:1.4,type:"triangle",gain:0.15},{beat:0,freq:C4,dur:1.4,type:"sine",gain:0.10},{beat:2,freq:A4,dur:1.6,type:"sine",gain:0.12}],
              [{beat:0,freq:C4,dur:2.4,type:"triangle",gain:0.15},{beat:0,freq:G4,dur:2.4,type:"sine",gain:0.10},{beat:2,freq:E5,dur:1.6,type:"sine",gain:0.13}] ] },
  };

  var sch = { track: null, bar: 0, nextTime: 0, droneOsc: null, droneGain: null };
  function startBgm(name) {
    stopDrone();
    var t = TRACKS[name]; if (!t) { sch.track = null; return; }
    sch.track = t; sch.bar = 0; sch.nextTime = now() + 0.1;
    // drone
    var o = AC.createOscillator(), g = AC.createGain();
    o.type = "sine"; o.frequency.value = t.drone; g.gain.value = 0.0001;
    o.connect(g); g.connect(musicGain); o.start();
    g.gain.setTargetAtTime(t.dgain, now(), 0.6);
    sch.droneOsc = o; sch.droneGain = g;
  }
  function stopDrone() {
    if (sch.droneGain) { sch.droneGain.gain.setTargetAtTime(0.0001, now(), 0.3); }
    if (sch.droneOsc) { try { sch.droneOsc.stop(now() + 0.8); } catch (e) {} }
    sch.droneOsc = null; sch.droneGain = null;
  }
  function runScheduler() {
    if (scheduler) return;
    scheduler = setInterval(function () {
      if (!AC || !sch.track) return;
      var lookahead = now() + 0.4;
      while (sch.nextTime < lookahead) {
        var t = sch.track, beatDur = 1 / t.tempo, barStart = sch.nextTime;
        var notes = t.bars[sch.bar % t.bars.length];
        notes.forEach(function (n) { tone(n.freq, barStart + n.beat * beatDur, n.dur, n.type, n.gain, musicGain); });
        sch.nextTime = barStart + 4 * beatDur;
        sch.bar++;
      }
    }, 120);
  }
  function bgm(name) {
    curBgm = name || null;
    if (!started) return;
    // brief music duck then swap
    if (musicGain) musicGain.gain.setTargetAtTime(0.0001, now(), 0.08);
    setTimeout(function () {
      if (!AC) return;
      startBgm(curBgm);
      musicGain.gain.setTargetAtTime(0.42, now(), 0.4);
    }, 180);
  }

  /* ---------- ambient beds (looping filtered noise) ---------- */
  function startAmb(name) {
    stopAmbVoice();
    if (!name) return;
    var src = AC.createBufferSource(); src.buffer = noiseBuffer(3); src.loop = true;
    var filt = AC.createBiquadFilter(), g = AC.createGain(), lfo = null, lfoG = null;
    g.gain.value = 0.0001; src.connect(filt); filt.connect(g); g.connect(ambGain);
    var target = 0.5;
    if (name === "windlow") { filt.type = "lowpass"; filt.frequency.value = 500; target = 0.35; }
    else if (name === "tundra") { filt.type = "bandpass"; filt.frequency.value = 700; filt.Q.value = 0.7; target = 0.5; }
    else if (name === "sea") { filt.type = "lowpass"; filt.frequency.value = 420; target = 0.6;
      lfo = AC.createOscillator(); lfoG = AC.createGain(); lfo.frequency.value = 0.18; lfoG.gain.value = 0.28;
      lfo.connect(lfoG); lfoG.connect(g.gain); lfo.start(); }
    else if (name === "underwater") { filt.type = "lowpass"; filt.frequency.value = 240; target = 0.55; }
    else if (name === "dogs") { filt.type = "bandpass"; filt.frequency.value = 900; target = 0.25; }
    else if (name === "sky") { filt.type = "highpass"; filt.frequency.value = 2200; target = 0.18;
      lfo = AC.createOscillator(); lfoG = AC.createGain(); lfo.frequency.value = 0.5; lfoG.gain.value = 0.12;
      lfo.connect(lfoG); lfoG.connect(g.gain); lfo.start(); }
    src.start();
    g.gain.setTargetAtTime(target, now(), 0.8);
    ambVoice = { src: src, g: g, lfo: lfo };
  }
  function stopAmbVoice() {
    if (!ambVoice) return;
    var v = ambVoice; ambVoice = null;
    try { v.g.gain.setTargetAtTime(0.0001, now(), 0.4); } catch (e) {}
    try { v.src.stop(now() + 0.9); } catch (e) {}
    if (v.lfo) try { v.lfo.stop(now() + 0.9); } catch (e) {}
  }
  function amb(name) { curAmb = name || null; if (started) startAmb(curAmb); }

  /* ---------- SFX ---------- */
  function ping(freq, t, dur, type, gain) { tone(freq, t, dur, type, gain, sfxGain); }
  function noiseHit(t, dur, freq, type, gain) {
    var s = AC.createBufferSource(); s.buffer = noiseBuffer(dur + 0.05);
    var f = AC.createBiquadFilter(), g = AC.createGain();
    f.type = type || "bandpass"; f.frequency.value = freq || 800; f.Q.value = 0.8;
    s.connect(f); f.connect(g); g.connect(sfxGain);
    g.gain.setValueAtTime(gain || 0.5, t); g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    s.start(t); s.stop(t + dur + 0.05);
  }
  var SFX = {
    text_blip: function (t) { ping(660, t, 0.06, "square", 0.10); },
    word_learned: function (t) { ping(880, t, 0.12, "sine", 0.22); ping(1320, t + 0.08, 0.16, "sine", 0.16); },
    correct: function (t) { ping(784, t, 0.1, "sine", 0.22); ping(1176, t + 0.06, 0.14, "sine", 0.18); noiseHit(t, 0.08, 1200, "bandpass", 0.15); },
    wrong: function (t) { ping(180, t, 0.18, "sawtooth", 0.18); noiseHit(t, 0.12, 200, "lowpass", 0.25); },
    enemy_hit: function (t) { noiseHit(t, 0.16, 500, "bandpass", 0.4); ping(240, t, 0.14, "square", 0.16); },
    enemy_defeated: function (t) { ping(392, t, 0.2, "sine", 0.2); ping(523, t + 0.12, 0.2, "sine", 0.2); ping(659, t + 0.24, 0.3, "sine", 0.22); noiseHit(t, 0.3, 300, "lowpass", 0.2); },
    levelup: function (t) { [523, 659, 784, 1046].forEach(function (f, i) { ping(f, t + i * 0.08, 0.18, "triangle", 0.2); }); },
    menu_click: function (t) { ping(520, t, 0.04, "square", 0.12); },
    page_turn: function (t) { noiseHit(t, 0.22, 3000, "highpass", 0.18); },
    raven_caw: function (t) { var o = AC.createOscillator(), g = AC.createGain(); o.type = "sawtooth";
      o.frequency.setValueAtTime(520, t); o.frequency.exponentialRampToValueAtTime(300, t + 0.12); o.frequency.exponentialRampToValueAtTime(420, t + 0.2);
      o.connect(g); g.connect(sfxGain); g.gain.setValueAtTime(0.22, t); g.gain.exponentialRampToValueAtTime(0.0001, t + 0.26);
      o.start(t); o.stop(t + 0.3); noiseHit(t, 0.18, 1400, "bandpass", 0.12); },
    heartbeat: function (t) { ping(70, t, 0.14, "sine", 0.4); ping(70, t + 0.22, 0.16, "sine", 0.34); },
    sunrise_swell: function (t) { var o = AC.createOscillator(), g = AC.createGain(); o.type = "sine";
      o.frequency.setValueAtTime(196, t); o.frequency.exponentialRampToValueAtTime(523, t + 1.2);
      o.connect(g); g.connect(sfxGain); g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(0.3, t + 0.6); g.gain.exponentialRampToValueAtTime(0.0001, t + 1.6);
      o.start(t); o.stop(t + 1.7); [330, 415, 523].forEach(function (f) { ping(f, t + 0.6, 1.0, "sine", 0.08); }); },
    victory_jingle: function (t) { [523, 659, 784, 1046, 784, 1046].forEach(function (f, i) { ping(f, t + i * 0.11, 0.22, "triangle", 0.2); }); },
  };
  function sfx(name) {
    if (!AC || !started || !enabled) return;
    var f = SFX[name]; if (f) f(now() + 0.001);
  }

  window.Game = window.Game || {};
  window.Game.audio = { init: init, setEnabled: setEnabled, isEnabled: isEnabled, bgm: bgm, amb: amb, sfx: sfx };
})();
