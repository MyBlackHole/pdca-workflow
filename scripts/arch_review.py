"""架构审查辅助工具：git 热点定位与 HTML 报告渲染。

- `hotspots(root, *, days, limit)`：按近 N 天 git log 文件变更频次返回高变更路径。
- `render_html(candidates, *, metrics, title)`：生成自包含 HTML（Tailwind + Mermaid）。
- CLI：`arch_review.py --root <root> --out <html路径> [--days 30]`。
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def _run_git(root: Path, *args: str) -> str | None:
    """在仓库根执行 git，返回 stdout；失败返回 None（如非 git 仓库）。"""
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def hotspots(root: Path, *, days: int = 30, limit: int = 15) -> list[str]:
    """返回近 days 天内按变更频次降序的高变更相对路径。

    - 非 git 仓库或无可统计提交时返回 `[]`，调用方据此回退全量扫描。
    - 按文件路径聚合变更次数（同一次提交只计一次），取前 limit 名。
    """
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    output = _run_git(root, "log", "--since", since, "--name-only", "--pretty=format:")
    if output is None:
        return []
    counts: Counter[str] = Counter()
    seen_per_run: set[str] = set()
    for line in output.splitlines():
        line = line.strip()
        if not line:
            seen_per_run.clear()
            continue
        if line in seen_per_run:
            continue
        seen_per_run.add(line)
        counts[line] += 1
    return [path for path, _ in counts.most_common(limit)]


def _badge(strength: str) -> str:
    tone = {
        "Strong": "bg-emerald-100 text-emerald-800",
        "Worth exploring": "bg-amber-100 text-amber-800",
        "Speculative": "bg-slate-100 text-slate-600",
    }.get(strength, "bg-slate-100 text-slate-600")
    return f'<span class="inline-block px-2 py-0.5 rounded text-xs font-semibold {tone}">{strength}</span>'


def _card(candidate: dict[str, Any], index: int) -> str:
    mermaid = candidate.get("mermaid")
    diagram = ""
    if mermaid:
        diagram = (
            '<div class="mermaid rounded bg-slate-50 p-4">'
            f'{mermaid}'
            "</div>"
        )
    files = "".join(
        f'<li class="font-mono text-xs">{path}</li>' for path in candidate.get("files", [])
    )
    return f"""
<section class="candidate-card border rounded-lg p-6 shadow-sm">
  <div class="flex items-start justify-between gap-4">
    <h3 class="text-lg font-bold">C{index}. {candidate.get('title', 'Untitled')}</h3>
    {_badge(candidate.get('strength', 'Speculative'))}
  </div>
  <div class="mt-3 grid md:grid-cols-2 gap-4">
    <div>
      <p class="text-sm font-semibold text-slate-500">Files</p>
      <ul class="mt-1 list-disc pl-5">{files}</ul>
    </div>
    <div>
      <p class="text-sm font-semibold text-slate-500">Problem</p>
      <p class="mt-1 text-sm">{candidate.get('problem', '')}</p>
    </div>
    <div>
      <p class="text-sm font-semibold text-slate-500">Solution</p>
      <p class="mt-1 text-sm">{candidate.get('solution', '')}</p>
    </div>
    <div>
      <p class="text-sm font-semibold text-slate-500">Benefits</p>
      <p class="mt-1 text-sm">{candidate.get('benefits', '')}</p>
    </div>
  </div>
  <div class="mt-4">{diagram}</div>
</section>
"""


def render_html(
    candidates: list[dict[str, Any]],
    *,
    metrics: dict[str, Any],
    title: str,
) -> str:
    """生成自包含 HTML 报告字符串。"""
    cards = "\n".join(_card(c, i) for i, c in enumerate(candidates, 1))
    if not cards:
        cards = (
            '<section class="candidate-card border rounded-lg p-6 shadow-sm">'
            '<p class="text-sm text-slate-500">No candidates in this round — expand the scan scope or accept the baseline.</p>'
            "</section>"
        )
    metrics_json = json.dumps(metrics, ensure_ascii=False)
    top = metrics.get("top")
    top_line = "None"
    if top:
        match = next((c for c in candidates if c.get("id") == top), None)
        if match:
            top_line = f"C{candidates.index(match) + 1}: {match.get('title', '')}"
    return f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>mermaid.initialize({{startOnLoad: true}});</script>
</head>
<body class="bg-slate-50 text-slate-900">
<main class="max-w-4xl mx-auto py-10 px-4">
  <h1 class="text-3xl font-bold">{title}</h1>
  <div class="mt-6 bg-white rounded-lg p-6 shadow-sm" id="metrics" data-metrics='{metrics_json}'>
    <h2 class="text-xl font-bold">Metrics</h2>
    <ul class="mt-2 grid grid-cols-2 md:grid-cols-5 gap-3 text-center">
      <li class="bg-slate-100 rounded p-3"><div class="text-2xl font-bold">{metrics.get('candidates', 0)}</div><div class="text-xs">candidates</div></li>
      <li class="bg-emerald-50 rounded p-3"><div class="text-2xl font-bold">{metrics.get('strong', 0)}</div><div class="text-xs">Strong</div></li>
      <li class="bg-amber-50 rounded p-3"><div class="text-2xl font-bold">{metrics.get('worth', 0)}</div><div class="text-xs">Worth exploring</div></li>
      <li class="bg-slate-50 rounded p-3"><div class="text-2xl font-bold">{metrics.get('speculative', 0)}</div><div class="text-xs">Speculative</div></li>
      <li class="bg-blue-50 rounded p-3"><div class="text-sm font-bold">{top_line}</div><div class="text-xs">Top recommendation</div></li>
    </ul>
  </div>
  <div class="mt-6 space-y-6">{cards}</div>
</main>
</body>
</html>
"""


def collect_candidates(root: Path, *, threshold: int = 200) -> list[dict[str, Any]]:
    """按文件坏味（超过 threshold 行）自动生成深化候选。

    作为候选的非空数据源之一：超长文件通常是混合职责的浅模块，
    返回候选列表（problem/solution/benefits/strength），供报告渲染。
    """
    candidates: list[dict[str, Any]] = []
    for path in sorted((root / "scripts").glob("*.py")):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        if len(lines) > threshold:
            candidates.append(
                {
                    "id": f"smell-{path.stem}",
                    "title": f"Split oversized module {path.name}",
                    "files": [path.relative_to(root).as_posix()],
                    "problem": f"{len(lines)} lines — mixed responsibilities make the module shallow and hard to test at one seam",
                    "solution": "Extract the core behaviour behind one deep interface and split peripheral helpers",
                    "benefits": "Raises locality and leverage; tests gain a clean seam",
                    "strength": "Worth exploring",
                }
            )
    return candidates


def _metrics_for(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    strong = sum(1 for c in candidates if c.get("strength") == "Strong")
    worth = sum(1 for c in candidates if c.get("strength") == "Worth exploring")
    speculative = sum(1 for c in candidates if c.get("strength") == "Speculative")
    return {
        "candidates": len(candidates),
        "strong": strong,
        "worth": worth,
        "speculative": speculative,
        "top": candidates[0]["id"] if candidates else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an HTML architecture review report")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--title", default="Architecture Review")
    args = parser.parse_args()
    hot = hotspots(args.root, days=args.days)
    candidates = collect_candidates(args.root)
    metrics = _metrics_for(candidates)
    html = render_html(candidates, metrics=metrics, title=args.title)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html, encoding="utf-8")
    print(json.dumps({"status": "written", "out": str(args.out), "hotspots": hot, "candidates": len(candidates)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
