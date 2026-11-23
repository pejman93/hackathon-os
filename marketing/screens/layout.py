"""A bounding-box registry for the screen artwork: elements register where they land, and an overlap is an error instead of a surprise on the printed piece.
"""


class Layout:
    def __init__(self, name):
        self.name = name
        self.boxes = []
        self.problems = []

    def place(self, label, x, y, w, h, may_overlap=()):
        """Register a box. Reports any overlap that was not declared safe."""
        box = (x, y, x + w, y + h)
        for other_label, other in self.boxes:
            if other_label in may_overlap or label in may_overlap:
                continue
            ox = min(box[2], other[2]) - max(box[0], other[0])
            oy = min(box[3], other[3]) - max(box[1], other[1])
            if ox > 1 and oy > 1:                      # 1pt of slop for rounding
                self.problems.append(
                    f'{self.name}: {label!r} overlaps {other_label!r} '
                    f'by {ox:.0f}x{oy:.0f}pt')
        self.boxes.append((label, box))
        return box

    def text(self, c, label, x, baseline, text, font, size, **kw):
        """Register the ink box of a single line, not its layout box: cap height
        above the baseline, descender below."""
        w = c.stringWidth(text, font, size)
        return self.place(label, x, baseline - size * 0.24, w, size * 0.96, **kw)

    def lines(self, c, label, x, first_baseline, texts, font, size, leading, **kw):
        w = max((c.stringWidth(t, font, size) for t in texts), default=0)
        n = len(texts)
        bottom = first_baseline - (n - 1) * leading - size * 0.24
        return self.place(label, x, bottom, w, (n - 1) * leading + size * 0.96, **kw)

    def within(self, label, margin_x, margin_y, W, H):
        """Flag anything that leaves the safe area — screens crop edges."""
        for name, (x0, y0, x1, y1) in self.boxes:
            if name != label:
                continue
            if x0 < margin_x - 1 or x1 > W - margin_x + 1 or y0 < margin_y - 1 or y1 > H - margin_y + 1:
                self.problems.append(
                    f'{self.name}: {name!r} breaks the safe area '
                    f'({x0:.0f},{y0:.0f})-({x1:.0f},{y1:.0f})')
