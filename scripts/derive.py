#!/usr/bin/env python3
"""Phase 4: favicons, web, social, email and motion assets (SKILL §7).

Everything here composites the real exported vector logo onto a background.
No image model ever draws the logo.
"""
from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import avlogo as L  # noqa: E402

ROOT = L.ROOT
KIT = ROOT / "AV-Brand-Kit"
LAY = KIT / "00_Master/layouts"
BG = ROOT / "assets/backgrounds"
IM = "magick" if shutil.which("magick") else "convert"
FFMPEG = "ffmpeg" if shutil.which("ffmpeg") else "/opt/pw-browsers/ffmpeg-1011/ffmpeg-linux"

GREEN, CREAM, GOLD, WHITE = L.C["green"], L.C["cream"], L.C["gold"], L.C["white"]


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"{' '.join(str(c) for c in cmd[:5])}... :\n{r.stderr[-700:]}")


def ink(src: pathlib.Path, out: pathlib.Path, *extra: str) -> pathlib.Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    run(["inkscape", str(src), "--export-type=png", *extra, "-o", str(out)])
    return out


def layout(name: str, mode: str) -> pathlib.Path:
    return LAY / f"AV_{name}_{mode}.svg"


def size_of(p: pathlib.Path) -> tuple[int, int]:
    cmd = ([IM, "identify", "-format", "%w %h", str(p)] if IM == "magick"
           else ["identify", "-format", "%w %h", str(p)])
    w, h = subprocess.run(cmd, capture_output=True, text=True).stdout.split()
    return int(w), int(h)


def compose(bg: pathlib.Path, fg: pathlib.Path, out: pathlib.Path,
            gravity: str = "center", offset: str = "+0+0") -> pathlib.Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    run([IM, str(bg), str(fg), "-gravity", gravity, "-geometry", offset,
         "-composite", str(out)])
    return out


def logo_png(name: str, mode: str, width: int, tmp: pathlib.Path) -> pathlib.Path:
    return ink(layout(name, mode), tmp, f"--export-width={width}",
               "--export-background-opacity=0")


TMP = ROOT / "assets/_tmp"


# ----------------------------------------------------------------- 02 favicons
def favicons() -> list[str]:
    out = KIT / "02_Favicon"
    out.mkdir(parents=True, exist_ok=True)
    made = []

    # monogram at 72 % of an opaque green square
    mono = logo_png("monogram_simple", "1c-cream", 738, TMP / "fav_mono.png")
    run([IM, "-size", "1024x1024", f"xc:{GREEN}", str(mono),
         "-gravity", "center", "-composite", str(out / "icon-1024.png")])
    made.append("icon-1024.png")

    src = out / "icon-1024.png"
    for px in (512, 192, 32, 16):
        run([IM, str(src), "-resize", f"{px}x{px}", str(out / f"icon-{px}.png")])
        made.append(f"icon-{px}.png")
    run([IM, str(src), "-resize", "180x180", str(out / "apple-touch-icon.png")])
    made.append("apple-touch-icon.png")
    run([IM, str(src), "-define", "icon:auto-resize=48,32,16", str(out / "favicon.ico")])
    made.append("favicon.ico")

    (out / "site.webmanifest").write_text(json.dumps({
        "name": "Auguste Viktoria Immobilien",
        "short_name": "Auguste Viktoria",
        "icons": [
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png",
             "purpose": "any maskable"},
        ],
        "theme_color": GREEN,
        "background_color": GREEN,
        "display": "standalone",
    }, indent=2) + "\n")
    made.append("site.webmanifest")

    (out / "head-snippet.html").write_text(f"""<!-- Auguste Viktoria Immobilien — favicon set.
     Copy these files to the web root, then paste this block into <head>. -->
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/icon-192.png" type="image/png" sizes="192x192">
<link rel="icon" href="/icon-512.png" type="image/png" sizes="512x512">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="{GREEN}">
""")
    made.append("head-snippet.html")
    return made


# ---------------------------------------------------------------------- 06 web
def web() -> list[str]:
    out = KIT / "06_Web"
    out.mkdir(parents=True, exist_ok=True)
    made = []

    for mode, label in (("full-dark", "dark"), ("full-light", "light")):
        shutil.copyfile(KIT / f"01_Logo/SVG/AV_horizontal_{mode}.svg",
                        out / f"header-{label}.svg")
        made.append(f"header-{label}.svg")

    # hero 1920x800, left third kept clear for text
    hero_bg = TMP / "hero_bg.png"
    run([IM, str(BG / "bg_hero_2400x1000.png"), "-resize", "1920x",
         "-gravity", "center", "-extent", "1920x800", str(hero_bg)])
    hero_logo = logo_png("stacked_tagline", "full-dark", 520, TMP / "hero_logo.png")
    compose(hero_bg, hero_logo, out / "hero_1920x800.jpg", "east", "+180+0")
    run([IM, str(out / "hero_1920x800.jpg"), "-quality", "88",
         str(out / "hero_1920x800.jpg")])
    made.append("hero_1920x800.jpg")

    # open graph 1200x630
    og_bg = TMP / "og_bg.png"
    run([IM, str(BG / "bg_wide_2048x1152.png"), "-resize", "1200x",
         "-gravity", "center", "-extent", "1200x630", str(og_bg)])
    og_logo = logo_png("horizontal", "full-dark", 720, TMP / "og_logo.png")
    compose(og_bg, og_logo, out / "og_1200x630.png")
    made.append("og_1200x630.png")

    # 9 % watermark
    wm = logo_png("monogram", "1c-cream", 3000, TMP / "wm.png")
    run([IM, str(wm), "-alpha", "set", "-channel", "A", "-evaluate", "multiply", "0.09",
         "+channel", str(out / "AV_watermark_9pct.png")])
    made.append("AV_watermark_9pct.png")

    (out / "README.md").write_text("""# 06_Web

| file | use |
|---|---|
| `header-dark.svg` | site header on the green / dark UI |
| `header-light.svg` | site header on white or cream |
| `hero_1920x800.jpg` | homepage hero. Left third is kept clear for a headline. |
| `og_1200x630.png` | Open Graph / Twitter card image |
| `AV_watermark_9pct.png` | 9 % opacity monogram for photo watermarking |

`hero_1920x800.jpg` uses a procedural background, not the photograph prompt P4
describes — no image-model key was available at build time. See
`assets/inbox/README.txt` to replace it.
""")
    made.append("README.md")
    return made


# ------------------------------------------------------------------- 03 social
def social() -> list[str]:
    out = KIT / "03_Social"
    out.mkdir(parents=True, exist_ok=True)
    made = []

    # profile: green field, gold ring at 86 % diameter, monogram_simple at 52 %
    ring = TMP / "ring.png"
    d = 1080
    r = int(d * 0.86)
    off = (d - r) // 2
    run([IM, "-size", f"{d}x{d}", f"xc:{GREEN}",
         "-fill", "none", "-stroke", GOLD, "-strokewidth", "8",
         "-draw", f"ellipse {d//2},{d//2} {r//2},{r//2} 0,360", str(ring)])
    pm = logo_png("monogram_simple", "1c-cream", int(d * 0.52), TMP / "prof_mono.png")
    compose(ring, pm, out / "profile_1080.png")
    shutil.copyfile(out / "profile_1080.png", out / "whatsapp_profile_1080.png")
    made += ["profile_1080.png", "whatsapp_profile_1080.png"]

    # LinkedIn banner: logo right-of-centre, left 30 % free for the profile photo
    li_bg = TMP / "li.png"
    run([IM, str(BG / "bg_wide_2048x1152.png"), "-resize", "1584x",
         "-gravity", "center", "-extent", "1584x396", str(li_bg)])
    li_logo = logo_png("horizontal", "full-dark", 700, TMP / "li_logo.png")
    compose(li_bg, li_logo, out / "linkedin_banner_1584x396.png", "east", "+90+0")
    made.append("linkedin_banner_1584x396.png")

    # Facebook cover
    fb_bg = TMP / "fb.png"
    run([IM, str(BG / "bg_wide_2048x1152.png"), "-resize", "820x",
         "-gravity", "center", "-extent", "820x312", str(fb_bg)])
    fb_logo = logo_png("horizontal", "full-dark", 560, TMP / "fb_logo.png")
    compose(fb_bg, fb_logo, out / "facebook_cover_820x312.png")
    made.append("facebook_cover_820x312.png")

    # Instagram post template: empty upper area, logo bottom-centre at 28 % width
    ig_bg = TMP / "ig.png"
    run([IM, str(BG / "bg_square_2048.png"), "-resize", "1080x1080!", str(ig_bg)])
    ig_logo = logo_png("stacked", "full-dark", int(1080 * 0.28), TMP / "ig_logo.png")
    compose(ig_bg, ig_logo, out / "instagram_post_1080.png", "south", "+0+84")
    made.append("instagram_post_1080.png")

    # Story: logo top-centre
    st_bg = TMP / "st.png"
    run([IM, str(BG / "bg_story_1080x1920.png"), "-resize", "1080x1920!", str(st_bg)])
    st_logo = logo_png("stacked_tagline", "full-dark", int(1080 * 0.46), TMP / "st_logo.png")
    compose(st_bg, st_logo, out / "instagram_story_1080x1920.png", "north", "+0+190")
    made.append("instagram_story_1080x1920.png")

    # Google Business
    gb = TMP / "gb.png"
    run([IM, "-size", "720x720", f"xc:{GREEN}", str(gb)])
    gb_logo = logo_png("monogram_simple", "1c-cream", int(720 * 0.62), TMP / "gb_logo.png")
    compose(gb, gb_logo, out / "google_business_logo_720.png")
    made.append("google_business_logo_720.png")

    gc_bg = TMP / "gc.png"
    run([IM, str(BG / "bg_wide_2048x1152.png"), "-resize", "1024x",
         "-gravity", "center", "-extent", "1024x576", str(gc_bg)])
    gc_logo = logo_png("stacked", "full-dark", 430, TMP / "gc_logo.png")
    compose(gc_bg, gc_logo, out / "google_business_cover_1024x576.png")
    made.append("google_business_cover_1024x576.png")
    return made


# -------------------------------------------------------------------- 05 email
def email() -> list[str]:
    out = KIT / "05_Templates/email"
    out.mkdir(parents=True, exist_ok=True)
    made = []

    banner = out / "banner_1200x400.png"
    bg = TMP / "email_bg.png"
    run([IM, "-size", "1200x400", f"xc:{GREEN}", str(bg)])
    lg = logo_png("horizontal_tagline", "full-dark", 820, TMP / "email_logo.png")
    compose(bg, lg, banner)

    if shutil.which("pngquant"):
        run(["pngquant", "--quality=65-90", "--speed", "1",
             str(banner), "-o", str(banner), "--force"])
    kb = banner.stat().st_size / 1024
    if kb >= 60:
        # fall back to the smaller render the skill prescribes
        run([IM, "-size", "1000x333", f"xc:{GREEN}", str(bg)])
        lg = logo_png("horizontal_tagline", "full-dark", 690, TMP / "email_logo.png")
        compose(bg, lg, banner)
        if shutil.which("pngquant"):
            run(["pngquant", "--quality=60-85", "--speed", "1",
                 str(banner), "-o", str(banner), "--force"])
        kb = banner.stat().st_size / 1024
        print(f"  banner reduced to 1000x333 -> {kb:.1f} KB")
    print(f"  banner_1200x400.png {kb:.1f} KB")
    made.append("banner_1200x400.png")

    (out / "signature.html").write_text(f"""<!-- Auguste Viktoria Immobilien — e-mail signature.
     Replace {{{{BANNER_URL}}}} with the hosted URL of banner_1200x400.png.
     Every [PLACEHOLDER] must be filled in before use. Table layout and inline CSS
     are deliberate: Outlook ignores <style> blocks and flexbox. -->
<table cellpadding="0" cellspacing="0" border="0" role="presentation"
       style="border-collapse:collapse;font-family:Montserrat,Arial,Helvetica,sans-serif;">
  <tr>
    <td style="padding:0 0 14px 0;">
      <img src="{{{{BANNER_URL}}}}" width="600" height="200" alt="Auguste Viktoria Immobilien"
           style="display:block;border:0;outline:none;text-decoration:none;width:600px;height:200px;">
    </td>
  </tr>
  <tr>
    <td style="padding:0 0 10px 0;border-top:1px solid {GOLD};"></td>
  </tr>
  <tr>
    <td style="font-size:15px;line-height:22px;color:{GREEN};font-weight:600;">
      [NAME]
    </td>
  </tr>
  <tr>
    <td style="font-size:13px;line-height:20px;color:#4a5a50;">
      [POSITION] &middot; Auguste Viktoria Immobilien [RECHTSFORM]
    </td>
  </tr>
  <tr>
    <td style="font-size:13px;line-height:20px;color:#4a5a50;padding-top:8px;">
      [STRASSE NR] &middot; [PLZ ORT]<br>
      T <a href="tel:[+49 ...]" style="color:{GREEN};text-decoration:none;">[+49 ...]</a>
      &middot;
      <a href="mailto:[info@...]" style="color:{GREEN};text-decoration:none;">[info@...]</a><br>
      <a href="https://[www....de]" style="color:{GOLD};text-decoration:none;">[www....de]</a>
    </td>
  </tr>
</table>
""")
    made.append("signature.html")
    return made


# ------------------------------------------------------------------- 09 motion
def motion() -> list[str]:
    out = KIT / "09_Motion"
    out.mkdir(parents=True, exist_ok=True)
    logo = logo_png("stacked_tagline", "full-dark", 900, TMP / "motion_logo.png")
    vf = ("[1]scale=900:-1,fade=in:st=0.3:d=1[l];"
          "[0][l]overlay=(W-w)/2:(H-h)/2,fade=out:st=3.2:d=0.8")
    made = []
    for name, codec, extra in (("AV_logo_intro.mp4", "libx264", ["-pix_fmt", "yuv420p"]),
                               ("AV_logo_intro.webm", "libvpx-vp9", ["-b:v", "1M"])):
        run([FFMPEG, "-y", "-loglevel", "error",
             "-f", "lavfi", "-i", f"color=c=0x{GREEN.lstrip('#')}:s=1920x1080:d=4",
             "-loop", "1", "-t", "4", "-i", str(logo),
             "-filter_complex", vf, "-c:v", codec, *extra, str(out / name)])
        made.append(name)
        print(f"  {name} {(out / name).stat().st_size // 1024} KB")
    return made


def main() -> None:
    TMP.mkdir(parents=True, exist_ok=True)
    total = 0
    for label, fn in (("02_Favicon", favicons), ("06_Web", web),
                      ("03_Social", social), ("05_Templates/email", email),
                      ("09_Motion", motion)):
        print(f"\n{label}:")
        made = fn()
        total += len(made)
        for m in made:
            print(f"  {m}")
    shutil.rmtree(TMP, ignore_errors=True)
    print(f"\n{total} files produced")


if __name__ == "__main__":
    main()
