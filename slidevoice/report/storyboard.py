"""Offline visual script review; all source text is escaped, never executable HTML."""

import html
import json
from pathlib import Path

from slidevoice.core.cache import atomic_text
from slidevoice.core.models import Project
from slidevoice.core.presentation import load_plan, load_targets


def write_storyboard(project: Project, root: Path, folder: Path) -> None:
    sections = []
    for slide in project.slides:
        plan = load_plan(root, slide.index)
        targets = {t.id: t for t in load_targets(root, slide.index)}
        buttons = []
        for i, beat in enumerate(plan.beats, 1):
            target = targets.get(beat.target_id or "")
            bounds = html.escape(
                json.dumps(target.bounds.model_dump() if target else None), quote=True
            )
            description = (
                f"{target.text} · {target.geometry_source}" if target else "Không nhấn vùng"
            )
            buttons.append(
                f'<button type="button" data-bounds="{bounds}" data-effect="{beat.effect}" aria-pressed="false">'
                f"<small>{i:02} · {html.escape(beat.purpose)} · {beat.effect}</small>"
                f"<span>{html.escape(beat.text)}</span><em>{html.escape(description)}</em></button>"
            )
        image = (
            html.escape("../../" + slide.image_path.as_posix(), quote=True)
            if slide.image_path
            else ""
        )
        warnings = " ".join(plan.warnings)
        sections.append(
            f"<section><h2>{slide.index:02} — {html.escape(slide.title)}</h2>"
            f'<p>{html.escape(plan.objective)}</p><div class="review">'
            f'<div class="canvas"><img src="{image}" alt="Slide {slide.index}">'
            '<div class="target" hidden></div></div><div class="beats">'
            + "".join(buttons)
            + f'</div></div><p class="warning">{html.escape(warnings)}</p></section>'
        )
    atomic_text(
        folder / "storyboard.html",
        """<!doctype html><html lang="vi"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SlideVoice · Duyệt vùng nhấn</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#0c1525;color:#e6edf9;font:16px/1.6 system-ui,sans-serif;padding:32px;max-width:1550px;margin:auto}
h1,h2{line-height:1.2}h1{font-size:36px}h2{font-size:24px}header,section{margin-bottom:36px}.muted,em{color:#9daec6}small{color:#5bcfcd;letter-spacing:.06em}
.review{display:grid;grid-template-columns:1.5fr 1fr;gap:24px;align-items:start}.canvas{position:relative;line-height:0;position:sticky;top:16px}.canvas img{width:100%;border-radius:8px}.target{position:absolute;border:2px solid #ffcf40;border-radius:8px;outline:4px solid #ffcf4018;pointer-events:none}
.beats{display:grid;gap:10px}button{font:inherit;text-align:left;padding:16px;border:1px solid #293b55;border-radius:12px;background:#142239;color:inherit;cursor:pointer}button:hover,button[aria-pressed=true]{border-color:#5bcfcd;background:#1a3046}button span,button em{display:block}em{font-size:13px;font-style:normal;margin-top:10px}.warning{color:#f3cc80}button:focus-visible{outline:3px solid #fff;outline-offset:2px}
@media(max-width:900px){body{padding:16px}.review{grid-template-columns:1fr}.canvas{position:relative;top:auto}}
</style><header><small>SLIDEVOICE / DIRECTOR REVIEW</small><h1>Duyệt lời giảng & vùng nhấn</h1>
<p class="muted">Bấm từng nhịp để xem vùng nguồn. Đây là preview hình học, chưa có thời gian audio và chưa phải chứng nhận chất lượng. Chữ xoay/nhóm hình chỉ có khung shape; không định vị từng từ.</p></header>"""
        + "".join(sections)
        + """<script>
document.querySelectorAll('section').forEach(section=>{
 section.querySelectorAll('button').forEach(button=>button.addEventListener('click',()=>{
  section.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
  const box=section.querySelector('.target'), bounds=JSON.parse(button.dataset.bounds);
  box.hidden=!bounds;if(!bounds)return;
  Object.assign(box.style,{left:bounds.x*100+'%',top:bounds.y*100+'%',width:bounds.width*100+'%',height:bounds.height*100+'%'});
 }));
});</script></html>""",
    )
