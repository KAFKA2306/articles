from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ARTICLE = Path("artifacts/candidates/2026-08/2026-08-13-chatgpt-multiproject-autonomy.md")
IMAGE_DIR = Path("images/chatgpt-multiproject-autonomy")
BASE = "/images/chatgpt-multiproject-autonomy/chatgpt-multiproject-autonomy-{:02d}.webp"

W, H = 1536, 1024
NAVY = "#12223a"
BLUE = "#215cd2"
GREEN = "#0d946c"
PURPLE = "#7447c8"
ORANGE = "#e98a12"
RED = "#dc3c3c"
GRAY = "#5a687c"
LINE = "#d2dae6"
BG = "#f7f9fc"
WHITE = "#ffffff"

def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKJP-Bold.otf" if bold else "/usr/share/fonts/opentype/noto/NotoSansCJKJP-Regular.otf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()

def wrap(draw: ImageDraw.ImageDraw, value: str, f: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in value.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        current = ""
        for ch in paragraph:
            trial = current + ch
            if draw.textbbox((0, 0), trial, font=f)[2] <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = ch
        if current:
            lines.append(current)
    return lines

def text(draw, xy, value, size, color=NAVY, bold=False, max_width=None, spacing=8):
    f = font(size, bold)
    x, y = xy
    lines = wrap(draw, value, f, max_width) if max_width else value.split("\n")
    for line in lines:
        draw.text((x, y), line, font=f, fill=color)
        y += size + spacing
    return y

def box(draw, rect, fill=WHITE, outline=LINE, width=3, radius=24):
    draw.rounded_rectangle(rect, radius=radius, fill=fill, outline=outline, width=width)

def arrow(draw, start, end, color=GRAY, width=7):
    import math
    draw.line((*start, *end), fill=color, width=width)
    x1, y1 = start
    x2, y2 = end
    ang = math.atan2(y2-y1, x2-x1)
    for delta in (2.55, -2.55):
        p = (x2 + 28*math.cos(ang+delta), y2 + 28*math.sin(ang+delta))
        draw.line((x2, y2, *p), fill=color, width=width)

def card(draw, rect, heading, body, accent=BLUE):
    box(draw, rect, fill=WHITE, outline=accent, width=3)
    x0, y0, x1, y1 = rect
    text(draw, (x0+28, y0+24), heading, 30, accent, True, x1-x0-56)
    text(draw, (x0+28, y0+78), body, 24, NAVY, False, x1-x0-56, 9)

def base(title: str, subtitle: str):
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    text(draw, (76, 42), title, 58, NAVY, True, 1380)
    text(draw, (78, 125), subtitle, 28, GRAY, False, 1380)
    return img, draw

def footer(draw, value):
    box(draw, (90, 890, 1446, 978), fill="#f0f5ff", outline="#c7d9fb", width=2, radius=22)
    text(draw, (125, 915), value, 27, NAVY, True, 1270)

def save(img, number):
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    path = IMAGE_DIR / f"chatgpt-multiproject-autonomy-{number:02d}.webp"
    img.save(path, "WEBP", quality=90, method=6)

def fig1():
    img, d = base("146個の個人開発を、ChatGPTで横断運用する", "repoごとに違う仕事を、GitHub上の状態から「次の1件」へつなぐ")
    labels = [("金融", GREEN), ("VR / 3D", PURPLE), ("ゲーム", RED), ("動画", BLUE), ("家計", ORANGE), ("情報", "#199a9a"), ("MCP / agent", "#3b68c9")]
    y = 225
    for i, (label, color) in enumerate(labels):
        x = 80 + (i % 2) * 360
        if i == 6:
            x, y = 80, 735
        else:
            y = 225 + (i // 2) * 160
        card(d, (x, y, x+320, y+125), label, "repo-xx   repo-yy   …", color)
    box(d, (850, 260, 1110, 690), fill=BG, outline="#91a0b6")
    text(d, (920, 300), "GitHub", 42, NAVY, True)
    for j, item in enumerate(["Issue", "PR", "Actions", "main"]):
        card(d, (885, 380+j*75, 1075, 442+j*75), item, "", BLUE if j < 3 else ORANGE)
    box(d, (1190, 310, 1435, 640), fill="#effbf7", outline=GREEN)
    text(d, (1240, 350), "ChatGPT", 38, NAVY, True)
    text(d, (1225, 445), "次の1件を選ぶ", 30, GREEN, True, 180)
    arrow(d, (1110, 480), (1190, 480), GREEN)
    footer(d, "ポイントは、AIが賢いことではなく、repo側が読める状態を出していること。")
    save(img, 1)

def fig2():
    img, d = base("813 PR の中身", "件数ではなく、Done条件まで到達した成果を見る")
    items = [
        ("finBI", "未来の金利データを公開前に検出\nfail-close", GREEN),
        ("rule-scribe-games", "320px崩れを原因特定から本番修復\nPlaywright + Production", PURPLE),
        ("travel", "公開後に再取得してSHA-256一致\nasset verify", BLUE),
        ("semiconductor-earnings-model", "private bucketへpublish後に全object検証\nOIDC", ORANGE),
    ]
    for i, (heading, body, color) in enumerate(items):
        x = 80 + (i % 2) * 720
        y = 235 + (i // 2) * 300
        card(d, (x, y, x+650, y+245), heading, body, color)
    footer(d, "AIがコードを書いた、ではなく「何をもって完了か」まで機械可読にした。")
    save(img, 2)

def fig3():
    img, d = base("finBI: 未来の金利を公開前に弾く", "point-in-time 検証は observation date ではなく availability timestamp で判定する")
    y = 430
    d.line((180, y, 1360, y), fill="#9aa7ba", width=8)
    pts = [(330, "retrieved_at\n2026-07-24 20:17Z", BLUE), (760, "observation_date\n2026-07-24", ORANGE), (1150, "availability\n2026-07-27 20:16Z", RED)]
    for x, label, color in pts:
        d.ellipse((x-20, y-20, x+20, y+20), fill=color)
        text(d, (x-150, y-135), label, 25, color, True, 300)
    card(d, (180, 560, 650, 710), "Snapshot", "DGS10 2026-07-24 = 4.69", BLUE)
    card(d, (720, 560, 1360, 710), "Source availability", "その値は 7/27 更新で初めて利用可能", RED)
    box(d, (160, 760, 1380, 855), fill="#fff2f2", outline=RED, width=3)
    text(d, (210, 785), "availability timestamp > retrieved_at  →  BLOCK", 34, RED, True, 1120)
    footer(d, "未来の値を含むsnapshotは公開せず、source vintageを確認できるまでfail-close。")
    save(img, 3)

def fig4():
    img, d = base("rule-scribe-games: 壊れた画面を本番まで直す", "見た目調整ではなく、CSS Grid の layout ownership を修正")
    card(d, (80, 230, 680, 680), "Before", "bodyにgrid / #root配下に実コンテンツ\n→ 全体が約320pxへ押し込まれる", RED)
    card(d, (850, 230, 1450, 680), "After", "#rootがgrid owner\nsidebar + main が正しい幅で配置", GREEN)
    arrow(d, (690, 455), (840, 455), GRAY)
    for i, (heading, body, color) in enumerate([("原因特定", "DOMとgrid itemの親子関係", RED), ("Playwright回帰", "1280px / 800px", PURPLE), ("Vercel Preview", "見た目と挙動", BLUE), ("Production", "HTTP 200", GREEN)]):
        x = 80 + i * 360
        card(d, (x, 730, x+320, 850), heading, body, color)
    footer(d, "layout ownershipを直し、production確認まで終えてDone。")
    save(img, 4)

def fig5():
    img, d = base("Prompt Vault → travel", "画像を配るだけでなく、公開後まで検証する")
    steps = [("Prompt Vault", "source asset", BLUE), ("lock", "source / destination SHA-256", PURPLE), ("travel", "deploy", BLUE), ("public URL", "re-download", GREEN), ("hash OK", "same bytes", GREEN)]
    for i, (heading, body, color) in enumerate(steps):
        x = 45 + i * 295
        card(d, (x, 330, x+250, 600), heading, body, color)
        if i < 4:
            arrow(d, (x+250, 465), (x+285, 465), GRAY, 6)
    footer(d, "source repo / consumer repo / production が同じものだと確認する。")
    save(img, 5)

def fig6():
    img, d = base("Control Plane / Data Plane", "状態と契約はGitHub、重い実体は別planeへ")
    card(d, (110, 260, 650, 760), "GitHub / Control Plane", "Issue\nPR\nActions\nmain\nprovenance / SHA-256", BLUE)
    card(d, (890, 260, 1430, 760), "Private Bucket / Data Plane", "artifact\ndata\nlarge snapshot\nobject verify", GREEN)
    arrow(d, (660, 420), (880, 420), BLUE)
    arrow(d, (880, 620), (660, 620), GREEN)
    text(d, (680, 355), "方針・状態", 26, BLUE, True)
    text(d, (685, 655), "成果物・データ", 26, GREEN, True)
    footer(d, "Gitは契約と証拠、Data Planeは大きな実体。役割を分けると横断制御しやすい。")
    save(img, 6)

def fig7():
    img, d = base("別々の分野が、同じ核へ収束する", "State / Contract / Evidence")
    card(d, (560, 340, 980, 690), "状態 / 契約 / 証拠", "機械が読める\n再実行できる\n完了を判定できる", BLUE)
    around = [("金融", "PIT / provenance", GREEN, (90, 210)), ("VR/3D", "artifact validation", PURPLE, (1080, 210)), ("ゲーム", "reproducible CI", RED, (90, 610)), ("情報", "canonical / projection", "#159d9d", (1080, 610)), ("家計", "privacy", ORANGE, (250, 760)), ("MCP", "least privilege", "#3b68c9", (930, 760))]
    for heading, body, color, (x, y) in around:
        card(d, (x, y, x+340, y+130), heading, body, color)
        arrow(d, (x+170, y+130 if y < 500 else y), (770, 500), color, 5)
    footer(d, "問題は違っても、「状態・契約・証拠を機械可読にする」方向は同じ。")
    save(img, 7)

def fig8():
    img, d = base("4つの横断状態", "生のGitHub状態を、行動できる状態へ圧縮する")
    states = [("working", "機械が次へ進められる", GREEN), ("waiting", "人間判断 or 外部待ち", ORANGE), ("done", "完了証拠がある", BLUE), ("failed", "失敗 or 再確認が必要", RED)]
    for i, (heading, body, color) in enumerate(states):
        x = 100 + (i % 2) * 720
        y = 250 + (i // 2) * 310
        card(d, (x, y, x+620, y+240), heading, body, color)
    footer(d, "状態が読めるから、次の1件を選べる。")
    save(img, 8)

def fig9():
    import math
    img, d = base("次を決めるループ", "コード生成の外側にあるオーケストレーション")
    steps = ["全体を見る", "次を選ぶ", "完了条件を読む", "実装する", "CIを確認", "merge", "production確認", "cleanup"]
    colors = [GREEN, GREEN, GREEN, BLUE, PURPLE, RED, ORANGE, PURPLE]
    cx, cy = 770, 520
    coords = []
    for i, step in enumerate(steps):
        a = -math.pi/2 + i * 2 * math.pi / len(steps)
        x = int(cx + 460 * math.cos(a))
        y = int(cy + 315 * math.sin(a))
        coords.append((x, y))
        card(d, (x-130, y-55, x+130, y+55), f"{i+1}", step, colors[i])
    for i in range(len(coords)):
        arrow(d, coords[i], coords[(i+1) % len(coords)], GREEN, 5)
    box(d, (650, 420, 890, 620), fill="#effbf7", outline=GREEN)
    text(d, (690, 465), "ChatGPT", 38, NAVY, True)
    text(d, (680, 530), "orchestration", 24, GREEN, True)
    footer(d, "repo内の自動化ではなく、repo間の「次」まで扱う。")
    save(img, 9)

def fig10():
    img, d = base("人間を消したのではない", "機械へ渡すもの / 人間へ残すもの")
    card(d, (90, 250, 700, 790), "機械へ", "繰り返し作業\nCI / test\nhash照合\n再現可能な検証", BLUE)
    card(d, (835, 250, 1445, 790), "人間へ", "売買判断\ncreative choice\n公開可否\n価値判断", GREEN)
    text(d, (725, 465), "≠", 56, GRAY, True)
    footer(d, "自律化とは、人間が毎回やらなくてよい仕事だけを外へ出すこと。")
    save(img, 10)

def generate_images():
    for fn in (fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10):
        fn()
    for number in range(1, 11):
        path = IMAGE_DIR / f"chatgpt-multiproject-autonomy-{number:02d}.webp"
        if not path.is_file() or path.stat().st_size == 0:
            raise SystemExit(f"missing generated image: {path}")

def embed_markdown():
    source = ARTICLE.read_text(encoding="utf-8")
    if source.count("published: false") != 1:
        raise SystemExit("publication gate changed")
    insertions = [
        ("この記事で書きたいのは、その理由だ。", "この記事で書きたいのは、その理由だ。\n\n![146個の個人開発をGitHubとChatGPTで横断運用する全体像](" + BASE.format(1) + ")"),
        ("実際に同じ時期に起きていたことは、もう少し種類が違う。", "実際に同じ時期に起きていたことは、もう少し種類が違う。\n\n![813 PRの中で達成された4つの具体的成果](" + BASE.format(2) + ")"),
        ("公開前にこれをblockerとして検出し、source availability / vintage timestampまで検証するfail-close契約と回帰testへ落とした。", "公開前にこれをblockerとして検出し、source availability / vintage timestampまで検証するfail-close契約と回帰testへ落とした。\n\n![finBIで未来の金利データを弾くpoint-in-time検証](" + BASE.format(3) + ")"),
        ("`#root` へgrid ownershipを移し、1280px / 800pxのPlaywright実寸回帰を追加し、Vercel PreviewとProduction deployを通し、公開 `/games/big-shot` とAPIのHTTP 200まで確認して完了にした。", "`#root` へgrid ownershipを移し、1280px / 800pxのPlaywright実寸回帰を追加し、Vercel PreviewとProduction deployを通し、公開 `/games/big-shot` とAPIのHTTP 200まで確認して完了にした。\n\n![rule-scribe-gamesの320pxレイアウト崩れを本番まで修復する流れ](" + BASE.format(4) + ")"),
        ("つまり、**source repoで正しい → consumer repoで正しい → 公開後も同じものが見えている**を一続きのDone条件にした。", "つまり、**source repoで正しい → consumer repoで正しい → 公開後も同じものが見えている**を一続きのDone条件にした。\n\n![Prompt Vaultからtravelへ共有画像を配布し公開後にhash検証する流れ](" + BASE.format(5) + ")"),
        ("2026年8月13日のscheduled Actions runでは、GitHub OIDCでprivate bucketへ認証し、allow-listされたprefixだけをexact mirrorし、**publish後にevery objectをverifyするところまで成功**した。", "2026年8月13日のscheduled Actions runでは、GitHub OIDCでprivate bucketへ認証し、allow-listされたprefixだけをexact mirrorし、**publish後にevery objectをverifyするところまで成功**した。\n\n![GitHubをControl Plane、private bucketをData Planeに分ける構成](" + BASE.format(6) + ")"),
        ("**異なるプロジェクトが、偶然同じアプリ構造になったのではない。異なる理由から「状態・契約・証拠を機械可読にする」方向へ寄っていった。**", "**異なるプロジェクトが、偶然同じアプリ構造になったのではない。異なる理由から「状態・契約・証拠を機械可読にする」方向へ寄っていった。**\n\n![金融・VR・ゲーム・情報・家計・MCPが状態・契約・証拠へ収束する図](" + BASE.format(7) + ")"),
        ("failed   = 失敗または再確認が必要\n```", "failed   = 失敗または再確認が必要\n```\n\n![working waiting done failedの4つの横断状態](" + BASE.format(8) + ")"),
        ("branch / PR / 一時ファイルをcleanupする\n↓\nもう一度全体を見る\n```", "branch / PR / 一時ファイルをcleanupする\n↓\nもう一度全体を見る\n```\n\n![ChatGPTが全体確認からcleanupまで次の仕事を選ぶ制御ループ](" + BASE.format(9) + ")"),
        ("意味・価値・不可逆性を含むもの\n→ 人間へ\n```", "意味・価値・不可逆性を含むもの\n→ 人間へ\n```\n\n![機械へ渡す仕事と人間へ残す判断の境界](" + BASE.format(10) + ")"),
    ]
    count = source.count("/images/chatgpt-multiproject-autonomy/")
    if count not in (0, 10):
        raise SystemExit(f"unexpected current image reference count: {count}")
    if count == 0:
        for old, new in insertions:
            if source.count(old) != 1:
                raise SystemExit(f"anchor count is not 1: {old[:80]!r}")
            source = source.replace(old, new, 1)
        ARTICLE.write_text(source, encoding="utf-8")
    final = ARTICLE.read_text(encoding="utf-8")
    if final.count("/images/chatgpt-multiproject-autonomy/") != 10:
        raise SystemExit("expected exactly 10 image references")
    if final.count("published: false") != 1:
        raise SystemExit("publication gate altered")

generate_images()
embed_markdown()
print("regenerated and embedded 10 deterministic illustrations")
