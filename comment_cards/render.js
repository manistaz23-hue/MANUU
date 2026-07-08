#!/usr/bin/env node
/**
 * Renders TikTok-style comment cards as crisp PNGs (transparent background)
 * for overlaying in the "Stay Ugly, Stay Alive" HeyGen video.
 *
 * Usage: node comment_cards/render.js
 * Output: comment_cards/out/card_01.png ... card_14.png + feed_screenshot.png
 */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const OUT = path.join(__dirname, 'out');

// Scene-mapped cards. Handles are fictional/anonymized on purpose.
const CARDS = [
  { n: 1,  user: 'stay.alive.club', creator: true,  time: '4d',  likes: '88.3K',
    text: "Give me your most \u{2728}unhinged\u{2728} survival hacks. I don’t mean “always keep pepper spray” I wanna know what unexpectedly saved your life!" },
  { n: 2,  user: 'finalgirl_energy', time: '4d', likes: '412.8K',
    text: "don’t scream “help.” scream FIRE. nobody comes for help — EVERYBODY comes to see a fire \u{1F525}" },
  { n: 3,  user: 'midwest.mama', time: '4d', likes: '389.1K',
    text: "scream “MOM.” every mother within a mile will turn around instantly." },
  { n: 4,  user: 'notyour.babe', time: '3d', likes: '356.7K',
    text: "never yell “leave me alone” — people think it’s a lovers’ spat. yell “I DON’T KNOW YOU.” people ACTIVATE for that." },
  { n: 5,  user: 'deb_from_hr', time: '4d', likes: '298.5K',
    text: "police officer told me: if he grabs you, DROP. go limp. it takes both his hands to move you and your mouth still works — scream." },
  { n: 6,  user: 'stay.alive.club', creator: true, pinned: true, time: '4d', likes: '431.2K',
    text: "be as disgusting as you can be. spit. slobber. bark. you can wash it all off later. Alive." },
  { n: 7,  user: 'spicy.paralegal', time: '3d', likes: '274.9K',
    text: "keep a bat in your car — WITH a glove and a ball ⚾ a bat alone is “premeditated.” the whole set means you were gonna play." },
  { n: 8,  user: 'cat.roommate', time: '3d', likes: '251.3K',
    text: "talk to your pet like a roommate. LOUD. “I’M HOME BABE, DON’T WAIT UP” — now the whole hallway thinks a man lives there." },
  { n: 9,  user: 'waitress.wisdom', time: '2d', likes: '226.8K',
    text: "decoy wallet with fake cash \u{1F4B8} and my tips ride home in a to-go box. robbers don’t want your leftovers \u{1F961}" },
  { n: 10, user: 'latte.and.chaos', time: '2d', likes: '198.4K',
    text: "secret fund he will NEVER know about. also it is free and 100% legal to lie to strangers about your name \u{1F92B}" },
  { n: 11, user: '911girlie', time: '2d', likes: '187.2K',
    text: "9-1-1 operator here: if you don’t know your location — mile markers, exit signs, store names. that’s how we find you." },
  { n: 12, user: 'aunt.jackie.energy', time: '2d', likes: '173.6K',
    text: "walk up to the nearest auntie: “MOM! this guy is bothering me!” congratulations, you’ve been adopted." },
  { n: 13, user: 'gutfeeling.gal', time: '1d', likes: '165.9K',
    text: "trust your gut. it’s a superpower. if it feels off, it IS off." },
  { n: 14, user: 'stay.alive.club', creator: true, time: '1d', likes: '92.7K',
    text: "drop YOUR most unhinged survival hack \u{1F447} the wildest ones make part 2" },
];

const AVATAR_GRADIENTS = [
  ['#f857a6', '#ff5858'], ['#7f7fd5', '#91eae4'], ['#f2994a', '#f2c94c'],
  ['#e96443', '#904e95'], ['#56ab2f', '#a8e063'], ['#fc466b', '#3f5efb'],
  ['#c94b4b', '#4b134f'], ['#00b09b', '#96c93d'], ['#ff416c', '#ff4b2b'],
  ['#8e2de2', '#4a00e0'], ['#11998e', '#38ef7d'], ['#f953c6', '#b91d73'],
  ['#f5af19', '#f12711'], ['#654ea3', '#eaafc8'],
];

const HEART = `<svg viewBox="0 0 48 48" class="heart"><path fill="currentColor" d="M24 42s-1.7-1.2-4.1-3.1C13 33.4 4 25.9 4 17.5 4 11.1 9 6 15.2 6c3.4 0 6.6 1.6 8.8 4.2C26.2 7.6 29.4 6 32.8 6 39 6 44 11.1 44 17.5c0 8.4-9 15.9-15.9 21.4C25.7 40.8 24 42 24 42z"/></svg>`;

function cardHTML(c, i) {
  const [g1, g2] = AVATAR_GRADIENTS[i % AVATAR_GRADIENTS.length];
  const initial = c.user.replace(/[^a-z]/gi, '').charAt(0).toUpperCase();
  return `
  <div class="card" id="card_${c.n}">
    ${c.pinned ? `<div class="pinned">\u{1F4CC} Pinned</div>` : ''}
    <div class="row">
      <div class="avatar" style="background:linear-gradient(135deg,${g1},${g2})">${initial}</div>
      <div class="body">
        <div class="user">${c.user}${c.creator ? '<span class="badge">· Creator</span>' : ''}</div>
        <div class="text">${c.text}</div>
        <div class="meta">${c.time} ago&nbsp;&nbsp;&nbsp;<span class="reply">Reply</span></div>
      </div>
      <div class="likes">${HEART}<div class="count">${c.likes}</div></div>
    </div>
  </div>`;
}

const CSS = `
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:transparent;
    font-family:'Liberation Sans','DejaVu Sans','Noto Color Emoji',sans-serif; }
  .card { width:660px; background:#1c1c1e; border-radius:18px;
    padding:20px 22px; margin:14px auto;
    box-shadow:0 8px 30px rgba(0,0,0,.45); }
  .pinned { color:#8a8a8e; font-size:15px; font-weight:700; margin:0 0 10px 66px; }
  .row { display:flex; align-items:flex-start; gap:14px; }
  .avatar { width:52px; height:52px; border-radius:50%; flex:0 0 52px;
    display:flex; align-items:center; justify-content:center;
    color:#fff; font-size:24px; font-weight:700; }
  .body { flex:1; min-width:0; }
  .user { color:#8a8a8e; font-size:17px; font-weight:700; margin-bottom:5px; }
  .badge { color:#ff2a55; font-weight:700; margin-left:6px; font-size:16px; }
  .text { color:#fff; font-size:21px; line-height:1.38; word-wrap:break-word; }
  .meta { color:#8a8a8e; font-size:16px; margin-top:9px; }
  .reply { font-weight:700; }
  .likes { flex:0 0 auto; display:flex; flex-direction:column; align-items:center;
    gap:4px; color:#8a8a8e; padding-top:4px; }
  .heart { width:26px; height:26px; }
  .count { font-size:15px; font-weight:600; }
  /* feed variant: opaque phone-screen background */
  body.feed { background:#121212; padding:26px 0; }
  body.feed .card { box-shadow:none; border-radius:0; margin:0 auto; background:#121212; }
  body.feed .header { color:#fff; text-align:center; font-size:19px; font-weight:700;
    padding:6px 0 18px; border-bottom:1px solid #2c2c2e; margin-bottom:6px; }
`;

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 2, viewport: { width: 760, height: 900 } });

  // 1) Individual transparent cards for video overlay
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>${CSS}</style></head>
    <body>${CARDS.map(cardHTML).join('\n')}</body></html>`;
  await page.setContent(html, { waitUntil: 'networkidle' });
  for (const c of CARDS) {
    const el = page.locator(`#card_${c.n}`);
    await el.screenshot({ path: path.join(OUT, `card_${String(c.n).padStart(2, '0')}.png`), omitBackground: true });
    console.log(`card_${String(c.n).padStart(2, '0')}.png`);
  }

  // 2) Full comment-section "screenshot" (stacked feed, dark background)
  const feedHtml = `<!doctype html><html><head><meta charset="utf-8"><style>${CSS}</style></head>
    <body class="feed"><div class="header">Comments (12.4K)</div>
    ${CARDS.map(cardHTML).join('\n')}</body></html>`;
  await page.setContent(feedHtml, { waitUntil: 'networkidle' });
  await page.locator('body').screenshot({ path: path.join(OUT, 'feed_screenshot.png') });
  console.log('feed_screenshot.png');

  await browser.close();
})();
