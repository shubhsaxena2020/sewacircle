# Build review sheets: one row per site (5 frames), 6 sites per sheet image.
import json, sys, os
from PIL import Image, ImageDraw
res = json.load(open(sys.argv[1], encoding='utf-8')); prefix = sys.argv[2]
ok = [r for r in res if r.get('ok')]
W, H = 300, 188
for s in range(0, len(ok), 6):
    rows = ok[s:s+6]; sheet = Image.new('RGB', (W*5, (H+22)*len(rows)), 'white'); d = ImageDraw.Draw(sheet)
    for i, r in enumerate(rows):
        y = i*(H+22)
        d.text((4, y+4), f"{r['title']} | webgl={r.get('webgl')} gsap={r.get('gsap')} vid={r.get('videos')} maxFont={r.get('maxFont')} fonts={','.join(r.get('fonts',[])[:3])}"[:240], fill='black')
        for k in range(5):
            p = f"shots/{r['id']}-{k}.jpg"
            if os.path.exists(p): sheet.paste(Image.open(p).resize((W, H)), (k*W, y+22))
    sheet.save(f"review/{prefix}-{s//6:02d}.jpg", quality=80)
print(len(ok), 'sites ->', (len(ok)+5)//6, 'sheets')
