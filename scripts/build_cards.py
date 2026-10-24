#!/usr/bin/env python3
"""
Terminal-style SVG cards for the artorias961 profile README.

Edit the CONTENT section below, then run from the repo root:

    pip install fonttools brotli
    python3 scripts/build_cards.py

Writes assets/hero.svg, assets/onefetch.svg, assets/neofetch.svg and
assets/stack.svg. JetBrains Mono (OFL-1.1, see scripts/fonts/OFL.txt) is
subset and embedded in every card, so the alignment looks the same on
every machine.
"""
from __future__ import annotations

import base64
import io
import pathlib
from xml.sax.saxutils import escape

from fontTools import subset

HERE = pathlib.Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
FONT_REGULAR = HERE / "fonts" / "JetBrainsMonoNL-Regular.woff2"
FONT_BOLD = HERE / "fonts" / "JetBrainsMonoNL-Bold.woff2"

# ─────────────────────────────── look ────────────────────────────────
W = 880                 # card width (px); README scales it to 100%
FS = 14                 # font size
CW = FS * 0.6           # JetBrains Mono advance width = 0.6 em
LH = FS * 1.32          # ascent + descent, so block-art rows touch
ASC = FS * 1.02         # baseline offset inside a row
PAD_X = 28
BAR_H = 34              # title bar
TOP = BAR_H + 18        # first text row starts here
BOTTOM = 20

# Tokyo Night — same theme as the github-readme-stats cards
COLORS = {
    "bg": "#1a1b26", "bar": "#16161e", "border": "#292e42",
    "fg": "#c0caf5", "sub": "#a9b1d6", "dim": "#565f89", "mute": "#737aa2",
    "r": "#f7768e", "o": "#ff9e64", "y": "#e0af68", "g": "#9ece6a",
    "t": "#73daca", "c": "#7dcfff", "b": "#7aa2f7", "m": "#bb9af7",
    # language dots
    "py": "#4b8bbe", "cc": "#a8b9cc", "cpp": "#f34b7d", "sh": "#89e051",
}
PALETTE_ROW_1 = ["#15161e", "#f7768e", "#9ece6a", "#e0af68", "#7aa2f7", "#bb9af7", "#7dcfff", "#a9b1d6"]
PALETTE_ROW_2 = ["#414868", "#ff899d", "#9fe044", "#faba4a", "#8db0ff", "#c7a9ff", "#a4daff", "#c0caf5"]

USER, HOST = "artorias961", "workstation"

# ────────────────────────────── CONTENT ──────────────────────────────
# A line is a list of segments. A segment is a plain string (default
# colour) or a (text, "classes") tuple. Classes: colour keys from COLORS
# plus "B" for bold.

HERO = [
    ("whoami", [
        [("Christopher Morales", "m B"), ("  ·  ", "dim"), "Python, Coffee, and Keyboard enthusiast"],
    ]),
    ("cat about.txt", [
        ["I’m an engineer who enjoys building real things at the intersection of"],
        [("hardware and software", "y B"), ". Many of my projects are inspired by ", ("video games", "m B"), ","],
        ["taking ideas from virtual worlds and turning them into physical systems."],
        ["I learn by building, breaking, and refining, driven mostly by curiosity"],
        ["and a simple ", ("“why not?”", "g B"), "."],
    ]),
    ("echo $MOTTO", [
        [("Just another engineer who likes building real things — one project at a time", "c")],
    ]),
]

# Chip logo: a coffee cup with a Python prompt, sitting on a QFP chip.
# Each row is (text, mask). Mask letters pick the colour of the character
# above them: s = steam, c = cup, p = prompt, _ = blinking cursor.
_LOGO = [
    ("  ▀▄ ▀▄ ▀▄   ", "  ss ss ss   "),
    ("▄▄▄▄▄▄▄▄▄▄▄  ", "ccccccccccc  "),
    ("█         █▀▄", "c         ccc"),
    ("█  >>> _  █▄▀", "c  ppp _  ccc"),
    ("▀▄▄▄▄▄▄▄▄▄▀  ", "ccccccccccc  "),
]
LOGO_LABEL = "CHRISTOPHER MORALES"
_MASK_CLASS = {" ": "fg", "s": "mute", "c": "m B", "p": "g B", "l": "c", "y": "y", "_": "fg"}


def _chip_art():
    """Returns (art rows, (row, col) of the blinking cursor inside the art)."""
    inner = 23
    pins_top = "  " + " " + "".join(" ╷" for _ in range(11)) + "  "
    pins_bot = "  " + " " + "".join(" ╵" for _ in range(11)) + "  "
    w = max(len(t) for t, _ in _LOGO)
    pad = (inner - w) // 2
    blank = (" " * inner, " " * inner)
    label = LOGO_LABEL.center(inner)
    body = [(" ●".ljust(inner), " y".ljust(inner)), blank]
    body += [((" " * pad + t).ljust(inner), (" " * pad + m).ljust(inner)) for t, m in _LOGO]
    body += [blank, (label, "".join("l" if ch != " " else " " for ch in label)), blank]

    art = [[(pins_top, "mute")],
           [("  ", ""), ("┌" + "─┴" * 11 + "─┐", "b")]]
    cursor = None
    for text, mask in body:
        if "_" in mask:
            cursor = (len(art), 3 + mask.index("_"))
            text = text.replace("_", " ")
        segs = [("──", "mute"), ("┤", "b")]
        segs += [(ch, _MASK_CLASS[m]) for ch, m in zip(text, mask)]
        segs += [("├", "b"), ("──", "mute")]
        art.append(segs)
    art += [[("  ", ""), ("└" + "─┬" * 11 + "─┘", "b")],
            [(pins_bot, "mute")]]
    return art, cursor


def _onefetch_info():
    k = lambda s: (s + ": ", "m B")  # noqa: E731
    title = [("artorias961", "m B"), (" ~ ", "fg"), ("Christopher Morales", "c B")]
    return [
        title,
        [("-" * 33, "sub")],
        [k("Project"), "hardware + software, one build at a time"],
        [k("HEAD"), ("c0ffee9", "y"), " (", ("main", "g"), ", ", ("origin/why-not", "r"), ")"],
        [k("Pending"), "C/C++, Zephyr RTOS, ROS, practical Linux"],
        [k("Topics"), "Embedded Systems, BLE, Wireless, Robotics"],
        [k("Languages")],
        [("   ", ""), ("● ", "py"), "Python  ", ("● ", "cc"), "C  ", ("● ", "cpp"), "C++  ", ("● ", "sh"), "Bash"],
        [k("Builds"), "embedded + firmware experiments"],
        [("        ", ""), "BLE tooling / device comms"],
        [("        ", ""), "robotics + sensors"],
        [("        ", ""), "DIY keyboards, electronics, “why not?” builds"],
        [k("Ask me about"), "Python, embedded dev, BLE, Linux workflows"],
        [k("Dependencies"), "coffee, music, late-night walks"],
        [k("Authors"), "100% Christopher Morales"],
        [k("Portfolio"), ("christopher-morales.vercel.app", "c")],
        [k("Inspired by"), "video games → physical systems"],
    ]


def _tower_art():
    w = 24  # interior width
    case = "sub"
    art = [[("╭" + "─" * w + "╮", case)],
           [("│", case), ("  ⏻  ", "g"), ("═ ═", "mute"), ("  ●".ljust(w - 8), "dim"), ("│", case)],
           [("├" + "─" * w + "┤", case)]]
    for _ in range(11):
        art.append([("│ ", case), ("▌" * 15, "o"), ("  ", ""), ("▒▒▒▒", "dim"), ("  ", ""), ("│", case)])
    art += [[("╰─┬" + "─" * (w - 4) + "┬─╯", case)],
            [("  ▀▀" + " " * (w - 4) + "▀▀", "dim")]]
    return art


def _neofetch_info():
    k = lambda s: (s + ": ", "b B")  # noqa: E731
    return [
        [(USER, "b B"), ("@", "fg"), (HOST, "b B")],
        [("-" * len(f"{USER}@{HOST}"), "sub")],
        [k("OS"), "Linux (daily driver)"],
        [k("Host"), "Fractal North · Charcoal Black"],
        [k("Board"), "ProArt Z890-CREATOR WIFI"],
        [k("CPU"), "Intel Core Ultra 7 265K"],
        [k("GPU"), "GIGABYTE GeForce RTX 5080"],
        [k("Memory"), "64GB DDR5"],
        [k("Disk (nvme0n1)"), "1TB WD Blue SN580"],
        [k("Disk (sda)"), "1TB Samsung SSD 860 EVO"],
        [k("PSU"), "Corsair RM1000x"],
        [k("Cooler"), "Noctua NH-D15"],
        [k("Shell"), "bash"],
        [k("Tools"), "git · docker · matlab"],
        [k("Hardware"), "raspberry pi · arduino"],
        [k("Web"), "react · redis"],
    ]


STACK = [
    ("embedded/", "C · C++ · Arduino", "firmware, protocols, device bring-up"),
    ("scripting/", "Python · Bash", "automation, testing, data parsing"),
    ("systems/", "Linux · Docker · Git", "workflows, containers, version control"),
    ("hw-diy/", "Raspberry Pi", "prototyping, tooling, side builds"),
]

# ───────────────────────────── renderer ──────────────────────────────


def _norm(segs):
    return [(s, "fg") if isinstance(s, str) else (s[0], s[1] or "fg") for s in segs]


class Card:
    def __init__(self, title: str, label: str):
        self.title, self.label = title, label
        self.defs: list[str] = []
        self.body: list[str] = []
        self.chars: set[str] = set(title)
        self.rows = 0

    # geometry
    @staticmethod
    def x(col):
        return PAD_X + col * CW

    @staticmethod
    def y(row):
        return TOP + row * LH + ASC

    @staticmethod
    def row_top(row):
        return TOP + row * LH

    def text(self, col, row, segs, attrs="", inner=""):
        merged = []
        for t, cls in _norm(segs):  # join neighbours with the same colour -> tidier markup
            if merged and merged[-1][1] == cls:
                merged[-1] = (merged[-1][0] + t, cls)
            elif t:
                merged.append((t, cls))
        segs = merged
        self.rows = max(self.rows, row + 1)
        spans = []
        for t, cls in segs:
            self.chars.update(t)
            spans.append(f'<tspan class="{cls}">{escape(t)}</tspan>')
        self.body.append(f'<text x="{self.x(col):.2f}" y="{self.y(row):.2f}"{attrs}>{inner}{"".join(spans)}</text>')

    def prompt(self, row, cmd="", attrs="", inner=""):
        p = [(USER, "g B"), ("@", "g B"), (HOST, "g B"), (":", "fg"), ("~", "b B"), ("$ ", "fg")]
        self.text(0, row, p, attrs, inner)
        plen = sum(len(t) for t, _ in p)
        if cmd:
            first, _, rest = cmd.partition(" ")
            self.text(plen, row, [(first, "c B"), (" " + rest if rest else "", "fg")])
        return plen

    def cursor(self, col, row, begin=0.0):
        self.rows = max(self.rows, row + 1)
        self.body.append(
            f'<rect x="{self.x(col):.2f}" y="{self.row_top(row) + 1:.2f}" width="{CW:.2f}" height="{LH - 2:.2f}" '
            f'fill="{COLORS["fg"]}" opacity="{0 if begin else 1}">'
            + (f'<set attributeName="opacity" to="1" begin="{begin:.2f}s" fill="freeze"/>' if begin else "")
            + f'<animate attributeName="opacity" values="1;0" calcMode="discrete" dur="1.1s" '
              f'begin="{begin:.2f}s" repeatCount="indefinite"/></rect>')

    def palette(self, col, row):
        for r, colours in enumerate((PALETTE_ROW_1, PALETTE_ROW_2)):
            for i, c in enumerate(colours):
                self.body.append(
                    f'<rect x="{self.x(col + i * 3):.2f}" y="{self.row_top(row + r):.2f}" '
                    f'width="{3 * CW:.2f}" height="{LH:.2f}" fill="{c}"/>')
        self.rows = max(self.rows, row + 2)

    def comment(self, note: str):
        self.body.append(f"\n  <!-- {note} -->")

    def svg(self, rows=None) -> str:
        rows = rows or self.rows
        h = round(TOP + rows * LH + BOTTOM)
        css = _font_css(self.chars)
        cls = "\n".join(f"    .{k:<6} {{ fill: {v}; }}" for k, v in COLORS.items())
        n = "\n  "
        bar = n.join([
            f'<path d="M0.5 10.5a10 10 0 0 1 10-10h{W - 21}a10 10 0 0 1 10 10v{BAR_H - 10.5}h-{W - 1}z" '
            f'fill="{COLORS["bar"]}"/>',
            f'<line x1="0.5" y1="{BAR_H}" x2="{W - 0.5}" y2="{BAR_H}" stroke="{COLORS["border"]}"/>',
            f'<circle cx="22" cy="{BAR_H / 2}" r="6" fill="#ff5f57"/>',
            f'<circle cx="42" cy="{BAR_H / 2}" r="6" fill="#febc2e"/>',
            f'<circle cx="62" cy="{BAR_H / 2}" r="6" fill="#28c840"/>',
            f'<text x="{W / 2}" y="{BAR_H / 2 + 4.5}" text-anchor="middle" class="dim" '
            f'style="font-size:12.5px">{escape(self.title)}</text>'])
        return f'''<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{escape(self.label)}">
<!--
  HOW TO EDIT THIS CARD BY HAND
  - Every line of the terminal is one <text> element below. Change the words
    between <tspan ...> and </tspan>.
  - Colours come from the class: fg (text), sub (light grey), dim / mute (grey),
    r (red), o (orange), y (yellow), g (green), t (teal), c (cyan), b (blue),
    m (purple). Add B for bold, e.g. class="m B".
  - Write & as &amp;  < as &lt;  > as &gt;
  - To add a row, copy a <text> line and add {LH:.2f} to its y value. If you add
    rows, also raise height="" and the viewBox height at the top by the same amount.
-->
  <title>{escape(self.label)}</title>
  <style>
    text {{
      font-family: "JBM", "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, "DejaVu Sans Mono", monospace;
      font-size: {FS}px; white-space: pre; fill: {COLORS["fg"]};
    }}
    .B      {{ font-weight: 700; }}
{cls}
  </style>
  <defs>{"".join(n + d for d in self.defs)}
  </defs>

  <!-- window -->
  <rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" rx="10" fill="{COLORS["bg"]}" stroke="{COLORS["border"]}"/>
  {bar}
{"".join(n + b if not b.startswith(chr(10)) else b for b in self.body)}

  <!-- font data (JetBrains Mono, OFL-1.1): leave this as is -->
  <style>{css}</style>
</svg>
'''


# glyphs always included, so hand edits with normal characters keep the same font
_ALWAYS = (set(map(chr, range(0x20, 0x7F))) | set("·’‘“”—–…→←↑↓✓✗●•×°±")
           | set(map(chr, range(0x2500, 0x25A0))))


def _font_css(chars: set[str]) -> str:
    text = "".join(sorted(chars | _ALWAYS))

    def sub(path):
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = []
        opts.hinting = False
        opts.desubroutinize = True
        font = subset.load_font(str(path), opts)
        s = subset.Subsetter(opts)
        s.populate(text=text)
        s.subset(font)
        buf = io.BytesIO()
        subset.save_font(font, buf, opts)
        return base64.b64encode(buf.getvalue()).decode()

    return "".join(
        f'@font-face{{font-family:"JBM";font-weight:{wt};'
        f'src:url(data:font/woff2;base64,{sub(p)}) format("woff2")}}'
        for wt, p in ((400, FONT_REGULAR), (700, FONT_BOLD)))


# ─────────────────────────────── cards ───────────────────────────────


def build_hero() -> str:
    card = Card(f"{USER}@{HOST}: ~", "Terminal: whoami — Christopher Morales, an engineer building at the "
                                     "intersection of hardware and software.")
    type_s, pause, line_s, gap = 0.055, 0.35, 0.07, 0.45
    t, row = 0.6, 0
    for i, (cmd, out) in enumerate(HERO):
        card.comment(f"$ {cmd}  (the <set> tags make lines appear in order)")
        shown = "" if i == 0 else f' opacity="0"'
        reveal = "" if i == 0 else f'<set attributeName="opacity" to="1" begin="{t - 0.15:.2f}s" fill="freeze"/>'
        plen = card.prompt(row, attrs=shown, inner=reveal)
        # typed command: clip a full-width text with a growing rect
        n = len(cmd)
        dur = n * type_s
        widths = ";".join(f"{k * CW:.2f}" for k in range(n + 1))
        cid = f"type{i}"
        card.defs.append(
            f'<clipPath id="{cid}"><rect x="{card.x(plen):.2f}" y="{card.row_top(row):.2f}" width="0" '
            f'height="{LH:.2f}"><animate attributeName="width" values="{widths}" calcMode="discrete" '
            f'begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>')
        first, _, rest = cmd.partition(" ")
        card.text(plen, row, [(first, "c B"), (" " + rest if rest else "", "fg")], f' clip-path="url(#{cid})"')
        # cursor that follows the typing, then disappears
        xs = ";".join(f"{card.x(plen + k):.2f}" for k in range(n + 1))
        end = t + dur + pause
        card.body.append(
            f'<rect x="{card.x(plen):.2f}" y="{card.row_top(row) + 1:.2f}" width="{CW:.2f}" '
            f'height="{LH - 2:.2f}" fill="{COLORS["fg"]}" opacity="0">'
            f'<set attributeName="opacity" to="1" begin="{max(t - 0.15, 0):.2f}s" fill="freeze"/>'
            f'<animate attributeName="x" values="{xs}" calcMode="discrete" begin="{t:.2f}s" '
            f'dur="{dur:.2f}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0" begin="{end:.2f}s" fill="freeze"/></rect>')
        row += 1
        t = end
        for line in out:
            card.text(0, row, line, ' opacity="0"',
                      f'<set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/>')
            row += 1
            t += line_s
        row += 1  # breathing room between commands
        t += gap
    card.comment("final prompt + blinking cursor")
    plen = card.prompt(row, attrs=' opacity="0"',
                       inner=f'<set attributeName="opacity" to="1" begin="{t - 0.15:.2f}s" fill="freeze"/>')
    card.cursor(plen, row, begin=t)
    return card.svg()


def build_onefetch() -> str:
    card = Card(f"{USER}@{HOST}: ~ — onefetch",
                "onefetch-style card: Christopher Morales. Interests: embedded systems, BLE, wireless, robotics. "
                "Learning C/C++, Zephyr RTOS, ROS and Linux. Languages: Python, C, C++, Bash. "
                "Portfolio: christopher-morales.vercel.app")
    card.comment("command")
    card.prompt(0, f"onefetch ~/{USER}")
    (art, cursor), info = _chip_art(), _onefetch_info()
    card.comment("logo: chip ASCII art (coffee cup + Python prompt)")
    for r, segs in enumerate(art):
        card.text(1, 2 + r, segs)
    if cursor:
        card.comment("blinking cursor inside the cup")
        card.text(1 + cursor[1], 2 + cursor[0], [("_", "fg B")],
                  inner='<animate attributeName="opacity" values="1;0" calcMode="discrete" '
                        'dur="1.1s" repeatCount="indefinite"/>')
    card.comment("info column")
    info_col = 1 + max(sum(len(t) for t, _ in _norm(s)) for s in art) + 4
    for r, segs in enumerate(info):
        card.text(info_col, 2 + r, segs)
    last = 2 + max(len(art), len(info) + 3)
    card.comment("colour palette")
    card.palette(info_col, 2 + len(info) + 1)
    card.comment("prompt + blinking cursor")
    plen = card.prompt(last + 1)
    card.cursor(plen, last + 1)
    return card.svg()


def build_neofetch() -> str:
    card = Card(f"{USER}@{HOST}: ~ — neofetch",
                "neofetch-style workstation specs: Linux, Intel Core Ultra 7 265K, GIGABYTE GeForce RTX 5080, "
                "64GB DDR5, ProArt Z890-CREATOR WIFI, Corsair RM1000x, Noctua NH-D15, Fractal North case.")
    card.comment("command")
    card.prompt(0, "neofetch")
    art, info = _tower_art(), _neofetch_info()
    card.comment("logo: PC tower ASCII art")
    for r, segs in enumerate(art):
        card.text(2, 2 + r, segs)
    card.comment("info column")
    info_col = 2 + max(sum(len(t) for t, _ in _norm(s)) for s in art) + 5
    for r, segs in enumerate(info):
        card.text(info_col, 2 + r, segs)
    card.comment("colour palette")
    card.palette(info_col, 2 + len(info) + 1)
    last = 2 + max(len(art), len(info) + 3)
    card.comment("prompt + blinking cursor")
    plen = card.prompt(last + 1)
    card.cursor(plen, last + 1)
    return card.svg()


def build_stack() -> str:
    card = Card(f"{USER}@{HOST}: ~ — tree",
                "Tools and tech: embedded (C, C++, Arduino), scripting (Python, Bash), "
                "systems (Linux, Docker, Git), hardware/DIY (Raspberry Pi).")
    card.comment("command + output")
    card.prompt(0, "tree ~/stack")
    card.text(0, 1, [(f"/home/{USER}/stack", "b B")])
    dw = max(len(d) for d, _, _ in STACK) + 3
    tw = max(len(t) for _, t, _ in STACK) + 3
    for i, (d, tools, why) in enumerate(STACK):
        branch = "└── " if i == len(STACK) - 1 else "├── "
        card.text(0, 2 + i, [(branch, "dim"), (d.ljust(dw), "b B"), (tools.ljust(tw), "y"), ("# " + why, "dim")])
    files = sum(len(t.split(" · ")) for _, t, _ in STACK)
    card.text(0, 3 + len(STACK), [f"{len(STACK)} directories, {files} files"])
    row = 5 + len(STACK)
    card.comment("prompt + blinking cursor")
    plen = card.prompt(row)
    card.cursor(plen, row)
    return card.svg()


def build_stats() -> str:
    card = Card(f"{USER}@{HOST}: ~ — stats", "Terminal: fetching GitHub stats for artorias961")
    card.prompt(0, f"./github-stats --user {USER} --theme tokyonight")
    card.text(0, 1, [("fetching stats, streak and top languages… ", "dim"), ("done ✓", "g B")])
    return card.svg()


def build_exit() -> str:
    card = Card(f"{USER}@{HOST}: ~", "Terminal: exit — thanks for stopping by, see you in the next build.")
    card.prompt(0, "exit")
    card.text(0, 1, [("logout", "sub")])
    card.text(0, 2, [(f"Connection to {USER} closed. ", "sub"),
                     ("Thanks for stopping by — see you in the next build.", "m")])
    return card.svg()


def main():
    ASSETS.mkdir(exist_ok=True)
    for name, fn in (("hero", build_hero), ("onefetch", build_onefetch),
                     ("neofetch", build_neofetch), ("stack", build_stack),
                     ("stats", build_stats), ("exit", build_exit)):
        svg = fn()
        (ASSETS / f"{name}.svg").write_text(svg, encoding="utf-8")
        print(f"assets/{name}.svg  {len(svg) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
