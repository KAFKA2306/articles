from __future__ import annotations

import base64
import hashlib
import json
import os
import urllib.request
from pathlib import Path

ARTICLE = Path("artifacts/candidates/2026-08/2026-08-13-chatgpt-multiproject-autonomy.md")
IMAGE_DIR = Path("images/chatgpt-multiproject-autonomy")
BASE = "/images/chatgpt-multiproject-autonomy/chatgpt-multiproject-autonomy-{:02d}.webp"
IMAGE_BLOBS = {
    1: "0f987483e084b660c0b31e982595f0cf9da8cf70",
    2: "dc40399af08c7c17e57ac35d06199de38cd80733",
    3: "9c3f313f5d49176d53856af9d93deea485bbf02f",
    4: "f487f173c5d288122c8affd8562967442efc9eee",
    5: "6232c38b74da6076a16fae37a8ea44c5fa879e04",
    6: "1e40287af1770d7e2ae002222cf838d0ed9a8683",
    7: "3d53d0ea02396f42c19b466bb58a80180951d6ac",
    8: "3eb94fec63a2dca52aff4820d4fcc5a67b8a596c",
    9: "ca81c7238ec7a23a7d63076987689807ee4bb78b",
    10: "4308375385348628373531a566fe615274c392ec",
}


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


def materialize_images() -> None:
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    for number, expected_sha in IMAGE_BLOBS.items():
        request = urllib.request.Request(
            f"https://api.github.com/repos/{repo}/git/blobs/{expected_sha}",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        with urllib.request.urlopen(request) as response:
            payload = json.load(response)
        data = base64.b64decode(payload["content"].replace("\n", ""))
        actual_sha = git_blob_sha(data)
        if actual_sha != expected_sha:
            raise SystemExit(f"blob mismatch for image {number}: {actual_sha} != {expected_sha}")
        target = IMAGE_DIR / f"chatgpt-multiproject-autonomy-{number:02d}.webp"
        target.write_bytes(data)


def embed_markdown() -> None:
    text = ARTICLE.read_text(encoding="utf-8")
    if "published: false" not in text:
        raise SystemExit("publication gate changed: expected published: false")

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

    current_count = text.count("/images/chatgpt-multiproject-autonomy/")
    if current_count not in (0, 10):
        raise SystemExit(f"unexpected current image reference count: {current_count}")
    if current_count == 0:
        for old, new in insertions:
            if text.count(old) != 1:
                raise SystemExit(f"anchor count is not 1: {old[:80]!r}")
            text = text.replace(old, new, 1)
        ARTICLE.write_text(text, encoding="utf-8")

    final = ARTICLE.read_text(encoding="utf-8")
    if final.count("/images/chatgpt-multiproject-autonomy/") != 10:
        raise SystemExit("expected exactly 10 image references")
    if final.count("published: false") != 1:
        raise SystemExit("publication gate was altered")


materialize_images()
embed_markdown()
print("materialized and embedded 10 illustrations")
