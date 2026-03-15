#!/usr/bin/env python3
"""
ICNASA Section 3 video production — Commercialisation Demo
6 scenes, ~115s, blurred background, Ken Burns effects, TTS narration.
Work dir: ~/s3_work/
"""
import os, json, subprocess, urllib.request, sys
from pathlib import Path
from gtts import gTTS

PYTHON  = sys.executable
TOKEN   = open(os.path.expanduser("~/.config/dropbox/token")).read().strip()
WORKDIR = Path.home() / "s3_work"
IMGDIR  = WORKDIR / "imgs"
CLIPDIR = WORKDIR / "clips"
for d in [WORKDIR, IMGDIR, CLIPDIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Dropbox helpers ───────────────────────────────────────────────────────────

def dbx_list(path):
    req = urllib.request.Request(
        "https://api.dropboxapi.com/2/files/list_folder",
        data=json.dumps({"path": path}).encode(),
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    )
    return json.loads(urllib.request.urlopen(req).read())["entries"]

def dbx_download(dbx_path, local_path):
    if Path(local_path).exists():
        return
    req = urllib.request.Request(
        "https://content.dropboxapi.com/2/files/download",
        headers={"Authorization": f"Bearer {TOKEN}",
                 "Dropbox-API-Arg": json.dumps({"path": dbx_path})}
    )
    with open(local_path, "wb") as f:
        f.write(urllib.request.urlopen(req).read())

def download_folder(dbx_folder, local_folder):
    local_folder = Path(local_folder)
    local_folder.mkdir(parents=True, exist_ok=True)
    entries = [e for e in dbx_list(dbx_folder) if e[".tag"] == "file"]
    print(f"  {len(entries)} files from {dbx_folder}", flush=True)
    for i, e in enumerate(entries):
        dbx_download(e["path_lower"], local_folder / e["name"])
        if (i+1) % 5 == 0:
            print(f"    downloaded {i+1}/{len(entries)}", flush=True)
    return sorted(str(local_folder / e["name"]) for e in entries)

# ── Download images ───────────────────────────────────────────────────────────

print("=== Downloading images ===", flush=True)

imgs_opening  = download_folder("/ICNASA2026/videos/image-final/2024/opening_ceremony",    IMGDIR/"opening")
imgs_hub      = download_folder("/ICNASA2026/videos/image-final/2025/hub_opening",         IMGDIR/"hub")
imgs_demo     = download_folder("/ICNASA2026/videos/image-final/2024/Demostration",        IMGDIR/"demo")
imgs_demo    += download_folder("/ICNASA2026/videos/image-final/2025/Demostration",        IMGDIR/"demo")
imgs_demo     = sorted(set(imgs_demo))
imgs_sponsor  = download_folder("/ICNASA2026/videos/image-final/2024/Industry_sponsor",    IMGDIR/"sponsor")
imgs_sponsor += download_folder("/ICNASA2026/videos/image-final/2025/Industry_sponsor",    IMGDIR/"sponsor")
imgs_sponsor  = sorted(set(imgs_sponsor))
imgs_students = download_folder("/ICNASA2026/videos/Images_sorted/2025/05_ANMFC_Students", IMGDIR/"students")
imgs_award    = download_folder("/ICNASA2026/videos/image-final/2024/Award",               IMGDIR/"award")
imgs_award   += download_folder("/ICNASA2026/videos/image-final/2025/Award",               IMGDIR/"award")
imgs_award    = sorted(set(imgs_award))

print(f"\nImages: opening={len(imgs_opening)} hub={len(imgs_hub)} demo={len(imgs_demo)} "
      f"sponsor={len(imgs_sponsor)} students={len(imgs_students)} award={len(imgs_award)}", flush=True)

# ── TTS narrations ────────────────────────────────────────────────────────────

NARRATIONS = {
    "3.1": (
        "The story of ICNASA begins with a landmark moment. "
        "In 2024, the Centre for Atomaterials and Nanomanufacturing was officially opened — "
        "a new home for cutting-edge research in Australia. "
        "Joined by industry leaders, government partners, and academic pioneers, "
        "this opening marked the beginning of a new era. "
        "From day one, ICNASA was built on collaboration between science and industry."
    ),
    "3.2": (
        "In 2025, ICNASA witnessed another milestone — the opening of the Industry Hub. "
        "A dedicated space where research meets industry, where breakthroughs become products, "
        "and where the gap between laboratory and market is bridged. "
        "The Hub stands as a living symbol of ICNASA's commitment to commercialisation "
        "and real-world impact."
    ),
    "3.3": (
        "At the heart of every ICNASA conference is the live demonstration floor — "
        "where ideas leave the page and come to life. "
        "Researchers present their latest prototypes and technologies side by side with industry partners, "
        "showcasing innovations in nanomanufacturing, advanced materials, and photonic devices. "
        "Attendees don't just hear about the future — they see it, touch it, and ask the hard questions. "
        "This direct exchange between lab and industry accelerates the path from discovery to deployment."
    ),
    "3.4": (
        "None of this is possible without the support of our industry sponsors. "
        "Companies and organisations from across Australia and the world have partnered with ICNASA, "
        "not just as funders, but as active contributors — co-designing research challenges, "
        "hosting demonstrations, and opening doors for graduates. "
        "Their investment is a vote of confidence in the power of advanced materials research "
        "to transform industries and improve lives."
    ),
    "3.5": (
        "ICNASA also looks to the future — literally. "
        "Students from across Australia visited the conference, getting their first glimpse "
        "of what a career in advanced manufacturing could look like. "
        "The spark of curiosity today is the breakthrough of tomorrow."
    ),
    "3.6": (
        "Excellence is celebrated at ICNASA. "
        "Best paper awards, innovation prizes, and industry commendations recognise "
        "the researchers and partners who are pushing boundaries. "
        "These moments of recognition fuel the drive to keep going — "
        "to solve harder problems, build better technologies, and make a greater impact."
    ),
}

print("\n=== Generating TTS ===", flush=True)
audio_files = {}
for sid, text in NARRATIONS.items():
    mp3 = WORKDIR / f"narr_{sid.replace('.','_')}.mp3"
    if not mp3.exists():
        gTTS(text=text, lang='en', tld='com.au').save(str(mp3))
        print(f"  {sid}: saved", flush=True)
    else:
        print(f"  {sid}: already exists", flush=True)
    audio_files[sid] = str(mp3)

def get_dur(path):
    r = subprocess.run(
        ["ffprobe","-v","quiet","-print_format","json","-show_format", str(path)],
        capture_output=True, text=True)
    return float(json.loads(r.stdout)["format"]["duration"])

durations = {k: get_dur(v) for k, v in audio_files.items()}
for k, d in durations.items():
    print(f"  Scene {k}: {d:.1f}s narration", flush=True)

# ── Blurred background Ken Burns clip ────────────────────────────────────────

# Stabilized motion profile to avoid perceived shaking
KB_MODES = ["zoomin_smooth"]

def make_img_clip(img, out_path, dur, mode="zoomin", w=1920, h=1080, fps=25):
    if Path(out_path).exists():
        return True
    fr = int(dur * fps)

    if mode == "zoomin_smooth":
        # Very gentle centered zoom to minimize perceived shaking
        zp = (f"zoompan=z='if(eq(on,1),1.0,min(zoom+0.00018,1.06))'"
              f":x='trunc(iw/2-(iw/zoom/2))':y='trunc(ih/2-(ih/zoom/2))':d={fr}:s={w}x{h}:fps={fps}")
    elif mode == "static":
        zp = (f"zoompan=z=1.0:x='trunc(iw/2-(iw/zoom/2))'"
              f":y='trunc(ih/2-(ih/zoom/2))':d={fr}:s={w}x{h}:fps={fps}")
    else:
        zp = (f"zoompan=z='if(eq(on,1),1.0,min(zoom+0.00015,1.05))'"
              f":x='trunc(iw/2-(iw/zoom/2))':y='trunc(ih/2-(ih/zoom/2))':d={fr}:s={w}x{h}:fps={fps}")

    # blurred bg: scale to fill, crop, blur
    # fitted fg:  scale to fit (letterbox/pillarbox), no distortion
    fc = (f"[0:v]split[bg][fg];"
          f"[bg]scale={w}:{h}:force_original_aspect_ratio=increase,"
          f"crop={w}:{h},gblur=sigma=15[blurbg];"
          f"[fg]scale={w}:{h}:force_original_aspect_ratio=decrease,"
          f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black@0[fitfg];"
          f"[blurbg][fitfg]overlay=0:0,{zp}[out]")

    cmd = ["ffmpeg", "-y", "-loop", "1", "-i", str(img),
           "-filter_complex", fc, "-map", "[out]",
           "-t", str(dur), "-r", str(fps),
           "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
           "-an", "-stats", str(out_path)]
    ret = subprocess.run(cmd).returncode
    if ret != 0:
        print(f"    Fallback (no KB): {os.path.basename(img)}", flush=True)
        fc2 = (f"[0:v]split[bg][fg];"
               f"[bg]scale={w}:{h}:force_original_aspect_ratio=increase,"
               f"crop={w}:{h},gblur=sigma=15[blurbg];"
               f"[fg]scale={w}:{h}:force_original_aspect_ratio=decrease,"
               f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2[fitfg];"
               f"[blurbg][fitfg]overlay=0:0[out]")
        cmd2 = ["ffmpeg","-y","-loop","1","-i",str(img),
                "-filter_complex",fc2,"-map","[out]",
                "-t",str(dur),"-r",str(fps),
                "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",
                "-an",str(out_path)]
        subprocess.run(cmd2)
    return Path(out_path).exists()

def make_scene(sid, images, audio_path, out_path, fps=25):
    if Path(out_path).exists():
        print(f"  Scene {sid}: already exists, skipping", flush=True)
        return
    total_dur = get_dur(audio_path) + 0.5
    n = len(images)
    per_img = total_dur / n
    print(f"\n--- Scene {sid}: {n} images, {total_dur:.1f}s total, {per_img:.2f}s/img ---", flush=True)

    tmp_clips = []
    for i, img in enumerate(images):
        mode = KB_MODES[i % len(KB_MODES)]
        clip = CLIPDIR / f"s{sid.replace('.','_')}_{i:02d}.mp4"
        print(f"  [{i+1}/{n}] {os.path.basename(img)} [{mode}]", flush=True)
        ok = make_img_clip(img, clip, dur=per_img, mode=mode, fps=fps)
        if not ok or not clip.exists():
            print(f"  WARNING: clip {i} failed, skipping image", flush=True)
            continue
        tmp_clips.append(str(clip))

    if not tmp_clips:
        print(f"  ERROR: no usable clips for scene {sid}", flush=True)
        return

    # concat clips
    no_audio = CLIPDIR / f"scene{sid.replace('.','_')}_noaudio.mp4"
    lst = CLIPDIR / f"scene{sid.replace('.','_')}_list.txt"
    with open(lst, "w") as f:
        for c in tmp_clips: f.write(f"file '{c}'\n")
    print(f"  Concatenating {n} clips...", flush=True)
    ret = subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),
                          "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",
                          "-stats",str(no_audio)]).returncode
    if ret != 0: print(f"  Concat failed", flush=True); return

    # add audio with fade-out
    audio_dur = get_dur(audio_path)
    vid_dur   = get_dur(no_audio)
    fade_st   = max(0, min(audio_dur, vid_dur) - 1.0)
    print(f"  Adding audio (fade out at {fade_st:.1f}s)...", flush=True)
    ret = subprocess.run([
        "ffmpeg","-y","-i",str(no_audio),"-i",str(audio_path),
        "-filter_complex",f"[1:a]afade=t=out:st={fade_st:.2f}:d=1.0[a]",
        "-map","0:v","-map","[a]",
        "-c:v","copy","-c:a","aac","-b:a","192k","-shortest",
        "-stats",str(out_path)
    ]).returncode
    if ret == 0:
        print(f"  ✓ Scene {sid}: {get_dur(out_path):.1f}s", flush=True)
    else:
        print(f"  ERROR: audio merge failed", flush=True)

# ── Produce all scenes ────────────────────────────────────────────────────────

print("\n=== Producing scenes ===", flush=True)
scenes = [
    ("3.1", imgs_opening,  audio_files["3.1"], CLIPDIR/"scene3_1.mp4"),
    ("3.2", imgs_hub,      audio_files["3.2"], CLIPDIR/"scene3_2.mp4"),
    ("3.3", imgs_demo,     audio_files["3.3"], CLIPDIR/"scene3_3.mp4"),
    ("3.4", imgs_sponsor,  audio_files["3.4"], CLIPDIR/"scene3_4.mp4"),
    ("3.5", imgs_students, audio_files["3.5"], CLIPDIR/"scene3_5.mp4"),
    ("3.6", imgs_award,    audio_files["3.6"], CLIPDIR/"scene3_6.mp4"),
]
for sid, imgs, audio, out in scenes:
    make_scene(sid, imgs, audio, out)

# ── Final concat ──────────────────────────────────────────────────────────────

print("\n=== Final concat ===", flush=True)
clip_paths = [out for _, _, _, out in scenes]
missing = [str(p) for p in clip_paths if not p.exists()]
if missing:
    print(f"Missing clips: {missing}"); sys.exit(1)

section3 = WORKDIR / "ICNASA_section3.mp4"
lst3 = WORKDIR / "section3_list.txt"
with open(lst3, "w") as f:
    for p in clip_paths: f.write(f"file '{p}'\n")
ret = subprocess.run([
    "ffmpeg","-y","-f","concat","-safe","0","-i",str(lst3),
    "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",
    "-c:a","aac","-b:a","192k","-stats",str(section3)
]).returncode
if ret != 0:
    print("ERROR: final concat failed"); sys.exit(1)

mb = section3.stat().st_size / 1024 / 1024
print(f"\n✓ ICNASA_section3.mp4: {get_dur(section3):.1f}s, {mb:.1f}MB", flush=True)

# ── Upload to Dropbox ─────────────────────────────────────────────────────────

print("\n=== Uploading to Dropbox ===", flush=True)
TOKEN2 = open(os.path.expanduser("~/.config/dropbox/token")).read().strip()
with open(section3, "rb") as f:
    data = f.read()
req = urllib.request.Request(
    "https://content.dropboxapi.com/2/files/upload",
    data=data,
    headers={"Authorization": f"Bearer {TOKEN2}",
             "Dropbox-API-Arg": json.dumps({"path": "/ICNASA2026/videos/ICNASA_section3.mp4", "mode": "overwrite"}),
             "Content-Type": "application/octet-stream"}
)
resp = json.loads(urllib.request.urlopen(req).read())
print(f"✓ Uploaded: {resp.get('name')} ({resp.get('size',0)//1024//1024}MB)", flush=True)
print("\nAll done.", flush=True)
