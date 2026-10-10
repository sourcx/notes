#!/usr/bin/env python3
"""Maak JPG-screenshots van video's, opgeslagen in <videonaam>-screenshots naast de video."""

import re
import subprocess
import sys
from pathlib import Path

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".mpg", ".mpeg", ".ts"}


def ask(prompt, default):
    answer = input(f"{prompt} [{default}]: ").strip()
    return answer or str(default)


def ask_number(prompt, default, cast=float):
    while True:
        try:
            value = cast(ask(prompt, default))
            if value > 0:
                return value
        except ValueError:
            pass
        print("Voer een positief getal in.")


def find_videos(directories):
    for directory in directories:
        for path in sorted(directory.rglob("*")):
            if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS:
                yield path


def build_filter(threshold, max_interval):
    # Altijd deinterlacen (ook vóór scene-detectie, tegen valse wissels door kamlijntjes).
    # Frame bij elke scene-wissel, bij het eerste frame, en minstens elke max_interval seconden.
    return (
        "yadif=mode=send_frame:parity=auto:deint=all,"
        f"select='gt(scene,{threshold})+isnan(prev_selected_t)"
        f"+gte(t-prev_selected_t,{max_interval})'"
    )


def format_timestamp(seconds):
    total = int(seconds)
    return f"{total // 3600:02d}h{total % 3600 // 60:02d}m{total % 60:02d}s"


def process(video, vf):
    out_dir = video.parent / f"{video.stem}-screenshots"
    if out_dir.exists() and any(out_dir.glob("*.jpg")):
        print(f"Overslaan (bestaat al): {out_dir}")
        return
    out_dir.mkdir(exist_ok=True)
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "info", "-y",
        "-i", str(video),
        "-vf", f"{vf},showinfo",
        "-q:v", "2",
    ]
    cmd += ["-fps_mode", "vfr"]
    cmd.append(str(out_dir / "tmp_%05d.jpg"))
    print(f"Verwerken: {video}")
    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    if "Nothing was written" in result.stderr:
        print("  Geen screenshots (geen scene-wissels gevonden)")
        out_dir.rmdir()
        return
    if result.returncode != 0:
        print(f"  Fout bij {video}:\n{result.stderr[-500:]}", file=sys.stderr)
        return

    times = [float(t) for t in re.findall(r"pts_time:\s*(-?[\d.]+)", result.stderr)]
    files = sorted(out_dir.glob("tmp_*.jpg"))
    if len(times) != len(files):
        print(f"  Waarschuwing: {len(files)} bestanden maar {len(times)} timestamps", file=sys.stderr)
    for i, (f, t) in enumerate(zip(files, times)):
        target = out_dir / f"{video.stem}_{format_timestamp(max(t, 0))}.jpg"
        n = 2
        while target.exists():
            target = out_dir / f"{video.stem}_{format_timestamp(max(t, 0))}-{n}.jpg"
            n += 1
        f.rename(target)
    print(f"  {len(files)} screenshots in {out_dir}")


def main():
    args = sys.argv[1:] or [ask("Directory met video's", ".")]
    directories = [Path(a).expanduser() for a in args]
    for d in directories:
        if not d.is_dir():
            sys.exit(f"Geen directory: {d}")

    threshold = ask_number("Gevoeligheid scene-detectie (0-1, lager = meer screenshots)", 0.3)
    max_interval = ask_number("Maximaal aantal seconden zonder screenshot", 60)
    vf = build_filter(threshold, max_interval)
    videos = list(find_videos(directories))
    if not videos:
        sys.exit("Geen video's gevonden.")
    for video in videos:
        process(video, vf)


if __name__ == "__main__":
    main()
