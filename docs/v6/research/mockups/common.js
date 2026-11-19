// Shared helpers for the mockups: paper people and ring builders (SVG strings).
window.person = (x, y, s, body, scarf, skin = '#C98B5E', hair = '#2B1D14') => `
<g transform="translate(${x} ${y}) scale(${s})" filter="url(#lift)">
  <path d="M-22 70 C-24 30 -14 18 0 18 C14 18 24 30 22 70 Z" fill="${body}"/>
  <path d="M-14 22 C-4 36 6 36 16 22 L18 30 C6 44 -6 44 -16 30 Z" fill="${scarf}"/>
  <circle cx="0" cy="0" r="15" fill="${skin}"/>
  <path d="M-15 -2 C-15 -18 15 -18 15 -2 C10 -10 -10 -10 -15 -2 Z" fill="${hair}"/>
</g>`;
window.ring = (cx, cy, r, seats, opts = {}) => {
  const petals = Array.from({ length: 36 }, (_, i) => {
    const a = i / 36 * Math.PI * 2, px = cx + Math.cos(a) * r, py = cy + Math.sin(a) * r * (opts.squash || 1);
    return `<ellipse cx="${px}" cy="${py}" rx="${r * 0.13}" ry="${r * 0.075}" transform="rotate(${a * 180 / Math.PI + 90} ${px} ${py})" fill="${i % 2 ? opts.c1 || '#F28C28' : opts.c2 || '#F6B13B'}"/>`;
  }).join('');
  const s = seats.map((st, i) => {
    const a = -Math.PI / 2 + i / seats.length * Math.PI * 2, px = cx + Math.cos(a) * r, py = cy + Math.sin(a) * r * (opts.squash || 1);
    return { x: px, y: py, ...st };
  });
  return { svg: `<g filter="url(#lift)">${petals}</g>`, seats: s };
};
