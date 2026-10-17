"""Installed-PowerPoint export and measured text-line geometry."""

import json
import os
from pathlib import Path

from slidevoice.core.errors import PluginUnavailable, StageFailed
from slidevoice.core.media import run_process
from slidevoice.core.models import Project, Slide
from slidevoice.core.registry import register
from slidevoice.plugins.render import FakeRenderer

EXPORT_SCRIPT = r"""
param([string]$Source, [string]$Destination, [int]$Width, [int]$Height)
$ErrorActionPreference = 'Stop'
$app = $null
$deck = $null
try {
    $app = New-Object -ComObject PowerPoint.Application
    $app.AutomationSecurity = 3
    $deck = $app.Presentations.Open($Source, -1, 0, 0)
    $lines = [System.Collections.Generic.List[object]]::new()
    $sw = [double]$deck.PageSetup.SlideWidth
    $sh = [double]$deck.PageSetup.SlideHeight
    for ($i = 1; $i -le $deck.Slides.Count; $i++) {
        $slide = $deck.Slides.Item($i)
        $name = Join-Path $Destination ('slide_{0:000}.png' -f $i)
        $slide.Export($name, 'PNG', $Width, $Height)
        foreach ($shape in $slide.Shapes) {
            # Groups/rotated/vertical text retain their coarse PPTX target.
            if ($shape.HasTextFrame -ne -1 -or $shape.Rotation -ne 0) { continue }
            if ($shape.TextFrame.HasText -ne -1 -or $shape.TextFrame.Orientation -ne 1) { continue }
            $range = $shape.TextFrame.TextRange
            for ($j = 1; $j -le $range.Lines().Count; $j++) {
                $line = $range.Lines($j, 1)
                $text = $line.Text.Trim()
                if (-not $text) { continue }
                $left = [double]$line.BoundLeft / $sw
                $top = [double]$line.BoundTop / $sh
                $lineWidth = [double]$line.BoundWidth
                # BoundHeight includes paragraph SpaceAfter on non-final lines.
                # Measure without that blank space, then restore in memory; never save.
                $after = $line.ParagraphFormat.SpaceAfter
                try {
                    $line.ParagraphFormat.SpaceAfter = 0
                    $lineHeight = [double]$line.BoundHeight
                } finally { $line.ParagraphFormat.SpaceAfter = $after }
                # Explicit doubles avoid PowerShell choosing the integer Math overload.
                $x = [Math]::Max(0.0, $left)
                $y = [Math]::Max(0.0, $top)
                $w = [Math]::Min(1.0, $left + $lineWidth / $sw) - $x
                $h = [Math]::Min(1.0, $top + $lineHeight / $sh) - $y
                if ($w -le 0 -or $h -le 0) { continue }
                $lines.Add(@{slide=$i; target=@{
                    id=('shape_{0}_line_{1}' -f $shape.Id, $j)
                    parent_id=('shape_{0}' -f $shape.Id)
                    text=$text; kind='text_line'; geometry_source='powerpoint_text_line'; is_text=$true
                    bounds=@{x=$x; y=$y; width=$w; height=$h}
                }})
            }
        }
    }
    $json = ConvertTo-Json -InputObject @($lines.ToArray()) -Depth 6
    [System.IO.File]::WriteAllText((Join-Path $Destination 'text_lines.json'), $json,
        [System.Text.UTF8Encoding]::new($false))
} finally {
    if ($null -ne $deck) { $deck.Close() }
    if ($null -ne $app) { $app.Quit() }
}
"""


@register("render", "powerpoint")
class PowerPointRenderer(FakeRenderer):
    name = "powerpoint"
    version = "0.2.2"

    def healthcheck(self) -> None:
        if os.name != "nt":
            raise PluginUnavailable("The powerpoint renderer requires Windows and PowerPoint.")

    def render(self, project: Project, out_dir: Path, width: int, height: int) -> list[Slide]:
        slides = super().render(project, out_dir, width, height)
        # Never allow the synthetic PNGs to masquerade as a successful export.
        for slide in slides:
            if slide.image_path:
                (self.workdir / slide.image_path).unlink()

        def literal(value: str) -> str:
            return "'" + value.replace("'", "''") + "'"

        command = (
            "& {"
            + EXPORT_SCRIPT
            + "} -Source "
            + literal(str((self.workdir / project.source_slides).resolve()))
            + " -Destination "
            + literal(str(out_dir.resolve()))
            + f" -Width {width} -Height {height}"
        )
        run_process(["powershell", "-NoProfile", "-NonInteractive", "-Command", command])
        if any(not (out_dir / f"slide_{s.index:03}.png").is_file() for s in slides):
            raise StageFailed("PowerPoint did not export every slide; no fake fallback is used.")
        try:
            lines = json.loads((out_dir / "text_lines.json").read_text(encoding="utf-8-sig"))
            if not isinstance(lines, list):
                raise ValueError("Expected an array")
        except (OSError, ValueError):
            raise StageFailed(
                "PowerPoint text-line export failed; no estimated bounds used."
            ) from None
        return slides
