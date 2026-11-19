from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFilter
root=Path(r'frontend/public/media/layers')
source=Path(r'docs/screens/v5/round4/source-frames')
assets=['dawn-board','youth-gather','turmeric-ring','crew-backups','ready-seal','drive-evidence','map-night']
for name in assets:
    im=Image.open(source/f'{name}.jpg').convert('RGB'); w,h=im.size
    im.save(root/f'{name}-base.webp','WEBP',quality=68,method=0)
    for layer,top,bottom in [('sky',0,.36),('mid',.19,.77),('foreground',.59,1.02)]:
        mask=Image.new('L',(w,h),0); d=ImageDraw.Draw(mask)
        upper=[(x,int(h*(top+.018*math.sin(x/w*8)))) for x in range(-50,w+51,80)]
        if layer=='sky':
            lower=[(x,int(h*(bottom+.018*math.sin(x/w*7+1)))) for x in range(w+50,-51,-80)]
            polygon=[(-50,-50),(w+50,-50)]+lower
        elif layer=='mid':
            lower=[(x,int(h*(bottom+.018*math.sin(x/w*7+1)))) for x in range(w+50,-51,-80)]
            polygon=upper+lower
        else: polygon=upper+[(w+50,h+50),(-50,h+50)]
        d.polygon(polygon,fill=255)
        mask=mask.filter(ImageFilter.GaussianBlur(8))
        layer_im=im.convert('RGBA'); layer_im.putalpha(mask)
        layer_im.save(root/f'{name}-{layer}.webp','WEBP',quality=68,method=0)
    print('done',name,flush=True)
print('total bytes',sum(p.stat().st_size for p in root.glob('*.webp')),flush=True)
