import os, random
from PIL import Image, ImageDraw
HOME = os.path.expanduser('~/tetris-cdi-tvos')
COLS = [(0, 200, 230), (250, 210, 0), (170, 60, 220), (60, 200, 80), (235, 50, 50), (40, 90, 230), (250, 140, 20)]

def block(d, x, y, s, c):
    d.rectangle([x, y, x + s - 1, y + s - 1], fill=c)
    b = max(2, s // 8)
    d.polygon([(x, y), (x + s, y), (x + s - b, y + b), (x + b, y + b), (x + b, y + s - b), (x, y + s)], fill=tuple(min(255, v + 70) for v in c))
    d.polygon([(x + s, y + s), (x, y + s), (x + b, y + s - b), (x + s - b, y + s - b), (x + s - b, y + b), (x + s, y)], fill=tuple(int(v * .55) for v in c))

def back(W, H):
    im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H; d.line([(0, y), (W, y)], fill=(int(10 + 20 * t), int(14 + 24 * t), int(48 + 60 * t)))
    s = H // 8
    for x in range(0, W, s): d.line([(x, 0), (x, H)], fill=(30, 40, 90))
    for y in range(0, H, s): d.line([(0, y), (W, y)], fill=(30, 40, 90))
    return im

def middle(W, H):                      # the settled stack at the bottom of the well
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    s = H // 8; random.seed(11)
    rows = [[1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1], [1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1]]
    ox = (W - 16 * s) // 2 if W >= 16 * s else -((16 * s - W) // 2)
    for r, row in enumerate(rows):
        for i, v in enumerate(row):
            if v and 0 <= ox + i * s < W: block(d, ox + i * s, H - (r + 1) * s, s, COLS[(i * 3 + r * 5) % 7])
    return im

def front(W, H):                       # a falling L piece with a CD ring behind it
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    s = H // 8; cx = W // 2; top = H // 8
    d.ellipse([cx - 2 * s - s // 2, top + s // 2, cx + 3 * s - s // 2, top + 5 * s + s // 2], outline=(230, 235, 255, 150), width=max(3, s // 6))
    for dx, dy in ((0, 0), (0, 1), (0, 2), (1, 2)): block(d, cx - s + dx * s, top + dy * s + s, s, COLS[4])
    for dx, dy in ((-3, 3), (-2, 3), (-1, 3), (-3, 4)): block(d, cx + dx * s + s, top + dy * s + s, s, COLS[1])
    return im

def scene(W, H):
    im = back(W, H).convert('RGBA'); im.alpha_composite(middle(W, H)); im.alpha_composite(front(W, H)); return im.convert('RGB')

def save_all(tree):
    base = os.path.join(tree, 'pkg/apple/tvOS/Assets.xcassets/App Icon & Top Shelf Image.brandassets')
    def put(path, img): img.save(path); print('wrote', os.path.relpath(path, base), img.size)
    for stack, sizes in (('App Icon.imagestack', {'': (400, 240), '-1': (800, 480)}), ('App Icon - App Store.imagestack', {'-1': (1280, 768)})):
        for layer, fn in (('Back', back), ('Middle', middle), ('Front', front)):
            for suf, (W, H) in sizes.items():
                img = fn(W * 2, H * 2).resize((W, H), Image.LANCZOS)
                if layer == 'Back': img = img.convert('RGB')
                put(os.path.join(base, stack, layer + '.imagestacklayer', 'Content.imageset', 'retroarch_logo_%s%s.png' % (layer.lower(), suf)), img)
    for d, items in (('Top Shelf Image.imageset', {'retroarch_720.png': (1920, 720), 'retroarch_1440.png': (3840, 1440)}), ('Top Shelf Image Wide.imageset', {'retroarch_720w.png': (2320, 720), 'retroarch_1440w.png': (4640, 1440)})):
        for name, (W, H) in items.items(): put(os.path.join(base, d, name), scene(W, H))

if __name__ == '__main__':
    os.makedirs(HOME + '/preview', exist_ok=True)
    scene(1280, 768).save(HOME + '/preview/icon.png')
    save_all(HOME + '/RetroArch')
