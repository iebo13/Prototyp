#!/usr/bin/env python3
"""Thin wrapper around the OpenAI Images API for the AV brand kit.

Used ONLY for the peacock feather (SKILL §3, prompt P1). The logo itself is never
generated or redrawn by an image model.

Defaults: model gpt-image-2, background="transparent", output_format="png",
the largest square size the API accepts.

Size discovery: the OpenAI API reference was not reachable from the build
environment (egress-blocked), so rather than hard-coding a guess this script
probes SIZE_CANDIDATES from largest to smallest and uses the first one the API
accepts. Pass --size to skip the probe.

Transparency fallback: if the API rejects background="transparent" with a 400,
the image is regenerated on a solid #00FF00 field and keyed out with the same
ffmpeg colorkey+despill chain the nano-banana CLI uses for its -t flag.

Usage:
    python3 scripts/gen_gpt_image.py --prompt-file assets/inbox/P1_feather.txt \
        --out assets/feather.png
"""
from __future__ import annotations

import argparse
import base64
import os
import pathlib
import shutil
import subprocess
import sys

# Largest first. gpt-image models have historically accepted 1024/1536/2048 squares;
# the probe below means a wrong guess costs one rejected request, not a wrong file.
SIZE_CANDIDATES = ["4096x4096", "2048x2048", "1536x1536", "1024x1024"]

P1 = (
    "Single peacock feather, flat vector illustration, exactly four flat colours: "
    "green #337B56, teal #21897F, gold #D1A976, dark green #062014. No gradients, "
    "no texture, no shading, hard clean edges. The feather curves gently up to the "
    "right like a calligraphic stroke, thin gold spine, one eye near the top. "
    "Isolated object, nothing else in frame."
)

GREEN_SCREEN = "#00FF00"


def _client():
    try:
        from openai import OpenAI
    except ImportError:
        sys.exit("openai package not installed: pip3 install openai")
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit(
            "OPENAI_API_KEY is not set.\n"
            "Either export it, or drop a hand-made/externally generated feather PNG "
            "into assets/inbox/ — see assets/inbox/README.txt."
        )
    return OpenAI()


def _is_bad_request(exc: Exception) -> bool:
    return getattr(exc, "status_code", None) == 400 or "400" in str(exc)


def _generate(client, prompt: str, model: str, size: str, background: str):
    kwargs = dict(model=model, prompt=prompt, size=size, output_format="png", n=1)
    if background:
        kwargs["background"] = background
    return client.images.generate(**kwargs)


def _write_b64(resp, dest: pathlib.Path) -> pathlib.Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(base64.b64decode(resp.data[0].b64_json))
    return dest


def _ffmpeg() -> str:
    for cand in ("ffmpeg", "/opt/pw-browsers/ffmpeg-1011/ffmpeg-linux"):
        if shutil.which(cand) or pathlib.Path(cand).is_file():
            return cand
    sys.exit("ffmpeg not found; cannot key the green screen.")


def _key_green_screen(src: pathlib.Path, dest: pathlib.Path) -> pathlib.Path:
    """colorkey + despill, matching the nano-banana -t behaviour."""
    vf = (
        "colorkey=0x00FF00:0.30:0.12,"
        "despill=type=green:mix=0.5:expand=0.3,"
        "format=rgba"
    )
    subprocess.run(
        [_ffmpeg(), "-y", "-loglevel", "error", "-i", str(src), "-vf", vf, str(dest)],
        check=True,
    )
    return dest


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--prompt", default=None, help="prompt text (defaults to P1)")
    ap.add_argument("--prompt-file", default=None, help="read the prompt from a file")
    ap.add_argument("--out", default="assets/feather.png")
    ap.add_argument("--model", default="gpt-image-2")
    ap.add_argument("--size", default=None, help="skip the size probe, e.g. 2048x2048")
    args = ap.parse_args()

    prompt = args.prompt or P1
    if args.prompt_file:
        prompt = pathlib.Path(args.prompt_file).read_text().strip()

    out = pathlib.Path(args.out)
    client = _client()
    sizes = [args.size] if args.size else SIZE_CANDIDATES

    last_error: Exception | None = None
    for size in sizes:
        # 1) preferred path: native transparency
        try:
            resp = _generate(client, prompt, args.model, size, "transparent")
            print(f"generated {size} with background=transparent")
            print(_write_b64(resp, out))
            return
        except Exception as exc:  # noqa: BLE001 - the API surfaces many error classes
            last_error = exc
            if not _is_bad_request(exc):
                raise
            print(f"  {size}: rejected ({exc}); trying green-screen fallback", file=sys.stderr)

        # 2) fallback: solid green screen, keyed out locally
        try:
            resp = _generate(
                client,
                f"{prompt} The background is a completely solid flat {GREEN_SCREEN} "
                f"chroma-key green field, edge to edge.",
                args.model,
                size,
                "",
            )
            raw = _write_b64(resp, out.with_name(out.stem + "_greenscreen.png"))
            print(f"generated {size} on green screen: {raw}")
            print(_key_green_screen(raw, out))
            return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if not _is_bad_request(exc):
                raise
            print(f"  {size}: rejected ({exc})", file=sys.stderr)

    sys.exit(f"all sizes rejected; last error: {last_error}")


if __name__ == "__main__":
    main()
