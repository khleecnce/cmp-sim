"""Digitise Sorooshian (2005) Figs 4.4-4.15 removal-rate scatter plots.

Chart geometry (verified per-image, not assumed):
  y: 9 horizontal gridlines, top = 4000 A/min, bottom = 0, step 500
  x: left frame = 0, right frame = 45000 Pa-m/s
  series colours: blue diamond = 40 rpm, red square = 80 rpm, black triangle = 120 rpm
Legend box is excluded by dropping blobs inside the detected legend rectangle.
"""
import numpy as np
from PIL import Image
import sys, os


def load(p):
    return np.asarray(Image.open(p).convert("RGB")).astype(int)


def calib(a):
    dark = a.sum(axis=2) < 450
    h, w = dark.shape
    rowsum = dark.sum(axis=1)
    colsum = dark.sum(axis=0)
    rows = np.where(rowsum > 0.8 * w)[0]
    cols = np.where(colsum > 0.8 * h)[0]
    # group consecutive rows
    grp, cur = [], [rows[0]]
    for r in rows[1:]:
        if r - cur[-1] <= 2:
            cur.append(r)
        else:
            grp.append(float(np.mean(cur))); cur = [r]
    grp.append(float(np.mean(cur)))
    gcol, cur = [], [cols[0]]
    for c in cols[1:]:
        if c - cur[-1] <= 2:
            cur.append(c)
        else:
            gcol.append(float(np.mean(cur))); cur = [c]
    gcol.append(float(np.mean(cur)))
    return grp, gcol


def blobs(mask, min_px=5):
    h, w = mask.shape
    seen = np.zeros_like(mask, bool)
    out = []
    for i in range(h):
        row = mask[i]
        for j in range(w):
            if row[j] and not seen[i, j]:
                stack = [(i, j)]; seen[i, j] = True; pts = []
                while stack:
                    y, x = stack.pop(); pts.append((y, x))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True; stack.append((ny, nx))
                if len(pts) >= min_px:
                    ys = np.array([p[0] for p in pts]); xs = np.array([p[1] for p in pts])
                    out.append(dict(cx=xs.mean(), cy=ys.mean(), n=len(pts),
                                    x0=xs.min(), x1=xs.max(), y0=ys.min(), y1=ys.max()))
    return out


def ycal(grows):
    """Fit the evenly spaced 500-A/min gridline ladder; return (y_of_zero, px_per_500).

    Some gridlines are hidden behind the legend box, and an outer figure border may
    also be detected, so the ladder is found as the largest set of rows sharing a
    common spacing rather than assumed to be complete.
    """
    best = None
    for i in range(len(grows)):
        for j in range(i + 1, len(grows)):
            step = (grows[j] - grows[i])
            for k in range(1, 6):
                s = step / k
                if s < 30:
                    continue
                inl = [r for r in grows if abs(((r - grows[i]) / s) - round((r - grows[i]) / s)) < 0.06]
                if best is None or len(inl) > len(best[0]):
                    best = (inl, s)
    inl, s = best
    inl = sorted(inl)
    # The detected ladder spans the full plot frame: top rule = 4000 A/min,
    # bottom rule (the x axis) = 0 A/min, in 500 A/min steps.
    span = inl[-1] - inl[0]
    nsteps = round(span / s)
    assert nsteps == 8, f"expected 8 gridline intervals (4000 A/min), got {nsteps}"
    return inl[-1], s, inl


def process(path, legend=None, verbose=True):
    a = load(path)
    grows, gcols = calib(a)
    xl, xr = gcols[0], gcols[-1]
    y_zero, step, ladder = ycal(grows)
    if verbose:
        print("###", os.path.basename(path))
        print("  rows:", [round(g, 1) for g in grows])
        print("  ladder:", [round(g, 1) for g in ladder], "step=%.2f px/500" % step,
              "y(0)=%.1f" % y_zero, " x frame:", xl, xr)
    ytop, ybot = y_zero - 8 * step, y_zero

    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    masks = {
        40: (b > 90) & (b - r > 45) & (b - g > 45),
        80: (r > 110) & (r - g > 55) & (r - b > 55),
        120: (r < 90) & (g < 90) & (b < 90),
    }

    # Locate the legend box from its horizontal rules: two dark runs of identical
    # length well short of the plot width, at the top and bottom of the box.
    if legend is None:
        dark = a.sum(axis=2) < 450
        runs = []
        for y in range(int(ytop) + 2, int(ybot) - 1):
            idx = np.where(dark[y, int(xl) + 1:int(xr)])[0]
            if len(idx) == 0:
                continue
            best = cur = 1
            start = bstart = idx[0]
            for k in range(1, len(idx)):
                if idx[k] == idx[k - 1] + 1:
                    cur += 1
                    if cur > best:
                        best, bstart = cur, start
                else:
                    cur, start = 1, idx[k]
            if 60 < best < 0.45 * (xr - xl):
                runs.append((y, best, bstart + int(xl) + 1))
        if len(runs) >= 2:
            y_top = runs[0][0]
            y_bot = runs[-1][0]
            x_a = min(r[2] for r in runs)
            x_b = max(r[2] + r[1] for r in runs)
            legend = (x_a - 4, y_top - 4, x_b + 5, y_bot + 5)
            if verbose:
                print("  legend box:", legend)

    res = {}
    for rpm, m in masks.items():
        m = m.copy()
        m[:, :int(xl) + 2] = False
        m[:, int(xr) - 1:] = False
        m[:int(ytop) + 2, :] = False
        m[int(ybot) - 1:, :] = False
        if legend:
            lx0, ly0, lx1, ly1 = legend
            m[ly0:ly1, lx0:lx1] = False
        pts = []
        for bl in blobs(m):
            wpx = bl["x1"] - bl["x0"] + 1
            hpx = bl["y1"] - bl["y0"] + 1
            if bl["n"] > 900 or wpx > 40 or hpx > 40:
                continue            # gridline fragments / axis debris, not markers
            X = (bl["cx"] - xl) / (xr - xl) * 45000.0
            Y = (ybot - bl["cy"]) / (ybot - ytop) * 4000.0
            pts.append((X, Y, bl["n"], hpx))
        pts.sort()
        res[rpm] = pts
        if verbose:
            print(f"  {rpm} rpm: {len(pts)} blobs")
            for X, Y, n, hpx in pts:
                print("     pV=%7.0f  RR=%6.0f   (px=%d, hpx=%d)" % (X, Y, n, hpx))
    return res


if __name__ == "__main__":
    args = sys.argv[1:]
    for p in args:
        process(p)
