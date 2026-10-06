#!/usr/bin/env python3
"""Monta slides e falas locais segundo a linha do tempo em JSON."""

import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import re
import subprocess
import wave


ROOT = Path(__file__).resolve().parents[2]
FPS = 30


def run(args):
    result = subprocess.run([str(arg) for arg in args], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-6000:])
    return result.stdout


def ffmpeg(*args):
    return run(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y", *args])


def probe(path):
    return json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format",
                           "-of", "json", path]))


def ffconcat(paths):
    return "ffconcat version 1.0\n" + "".join(
        "file '" + str(path).replace("'", "'\\''") + "'\n" for path in paths
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeline", type=Path, default=ROOT / "records/edicao.json")
    parser.add_argument("--build-dir", type=Path, default=ROOT / "build/video")
    parser.add_argument("--output", type=Path, default=ROOT / "records/apresentacao-final.mp4")
    parser.add_argument("--skip-render", action="store_true")
    args = parser.parse_args()
    timeline = json.loads(args.timeline.read_text())
    build = args.build_dir.resolve()
    build.mkdir(parents=True, exist_ok=True)
    frames = build / "frames"
    if not args.skip_render:
        run(["node", ROOT / "records/scripts/render_slides.cjs", "--output-dir", frames])

    sources = []
    audit = []
    for index, source in enumerate(timeline["audio"]):
        original = ROOT / source["file"]
        target = build / f"audio-{index:02d}.wav"
        filters = []
        if source.get("start", 0) or "end" in source:
            trim = f"atrim=start={source.get('start', 0)}"
            if "end" in source:
                trim += f":end={source['end']}"
            filters.extend([trim, "asetpts=PTS-STARTPTS"])
        # Medir em mono evita uma diferença de volume entre as fontes mono e estéreo.
        filters.append("aformat=channel_layouts=mono")
        measurement = subprocess.run(
            ["ffmpeg", "-nostdin", "-hide_banner", "-i", str(original), "-vn", "-af",
             ",".join(filters + ["loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json"]),
             "-f", "null", "-"], capture_output=True, text=True,
        )
        if measurement.returncode:
            raise RuntimeError(measurement.stderr[-6000:])
        matches = re.findall(r'\{\s*"input_i"[^}]+\}', measurement.stderr)
        if not matches:
            raise RuntimeError(f"Não foi possível medir o volume de {original.name}.")
        loudness = json.loads(matches[-1])
        if loudness["input_i"] == "-inf":
            raise ValueError(f"O arquivo {original.name} contém somente silêncio. Substitua a fonte antes de montar.")
        normalization = (
            "loudnorm=I=-16:TP=-1.5:LRA=11:linear=false"
            f":measured_I={loudness['input_i']}:measured_TP={loudness['input_tp']}"
            f":measured_LRA={loudness['input_lra']}:measured_thresh={loudness['input_thresh']}"
            f":offset={loudness['target_offset']}"
        )
        filters.extend([normalization, "aresample=48000"])
        ffmpeg("-i", original, "-vn", "-af", ",".join(filters), "-ac", "1", "-c:a", "pcm_s16le", target)
        with wave.open(str(target), "rb") as wav:
            duration = wav.getnframes() / wav.getframerate()
            samples = wav.readframes(wav.getnframes())
        if not any(samples):
            raise ValueError(f"O arquivo {original.name} contém somente silêncio. Substitua a fonte antes de montar.")
        sources.append(target)
        audit.append({"file": source["file"], "sha256": hashlib.sha256(original.read_bytes()).hexdigest(),
                      "duration": duration, "kind": source.get("kind", "gravacao"),
                      "input_loudness_mono_lufs": loudness["input_i"]})
    (build / "audio.ffconcat").write_text(ffconcat(sources))
    audio = build / "narracao.wav"
    ffmpeg("-f", "concat", "-safe", "0", "-i", build / "audio.ffconcat", "-c:a", "copy", audio)
    with wave.open(str(audio), "rb") as wav:
        total_duration = wav.getnframes() / wav.getframerate()

    events = timeline["visuals"]
    if not events or abs(events[0]["at"]) > 0.001:
        raise ValueError("A linha do tempo visual precisa começar em zero.")
    if any(a["at"] >= b["at"] for a, b in zip(events, events[1:])):
        raise ValueError("Os tempos das imagens precisam estar em ordem crescente.")
    if events[-1]["at"] >= total_duration:
        raise ValueError("A última imagem precisa começar antes do fim do áudio.")
    if total_duration > 600:
        raise ValueError(f"Duração {total_duration:.2f} s ultrapassa o limite de 10 minutos.")

    # Arredondar as posições, em vez das durações, evita acumular erro entre cenas.
    positions = [round(event["at"] * FPS) for event in events] + [round(total_duration * FPS)]
    clips = [build / f"cena-{i:03d}.mp4" for i in range(len(events))]

    def encode_scene(index):
        event = events[index]
        duration = (positions[index + 1] - positions[index]) / FPS
        image = frames / event["image"]
        if not image.exists():
            raise FileNotFoundError(image)
        command = ["-loop", "1", "-framerate", str(FPS), "-i", image]
        fade = 0.2 if index + 1 < len(events) and event.get("dissolve", True) else 0
        if fade and duration > fade:
            next_image = frames / events[index + 1]["image"]
            command.extend(["-loop", "1", "-framerate", str(FPS), "-i", next_image,
                            "-filter_complex_threads", "1", "-filter_complex",
                            f"[0:v]format=yuv420p,settb=AVTB[a];[1:v]format=yuv420p,settb=AVTB[b];"
                            f"[a][b]xfade=transition=fade:duration={fade}:offset={duration-fade:.6f}[v]",
                            "-map", "[v]"])
        else:
            command.extend(["-vf", "format=yuv420p"])
        command.extend(["-t", f"{duration:.6f}", "-an", "-c:v", "libx264", "-preset", "veryfast",
                        "-tune", "stillimage", "-crf", "19", "-threads", "2", "-r", str(FPS),
                        "-pix_fmt", "yuv420p", "-video_track_timescale", "30000", clips[index]])
        ffmpeg(*command)
        print(f"Cena {index+1}/{len(events)}: {event['image']} ({duration:.2f} s)", flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(encode_scene, range(len(events))))
    (build / "video.ffconcat").write_text(ffconcat(clips))
    metadata = [";FFMETADATA1", "title=Contagem de objetos em matrizes binárias — SISOP",
                "comment=Montagem dos slides locais e narração; consultar records/README.md para a origem das falas."]
    chapters = timeline["chapters"]
    for index, chapter in enumerate(chapters):
        end = chapters[index + 1]["at"] if index + 1 < len(chapters) else total_duration
        title = chapter["title"].replace("=", "\\=").replace(";", "\\;").replace("#", "\\#")
        metadata.extend(["[CHAPTER]", "TIMEBASE=1/1000", f"START={round(chapter['at']*1000)}",
                         f"END={round(end*1000)}", f"title={chapter['slide']:02d}. {title}"])
    (build / "capitulos.ffmetadata").write_text("\n".join(metadata) + "\n")
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    mux = ["-f", "concat", "-safe", "0", "-i", build / "video.ffconcat", "-i", audio,
           "-i", build / "capitulos.ffmetadata"]
    if timeline.get("subtitles"):
        mux.extend(["-i", ROOT / timeline["subtitles"]])
    mux.extend(["-map", "0:v:0", "-map", "1:a:0", "-map_metadata", "2", "-map_chapters", "2",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000"])
    if timeline.get("subtitles"):
        mux.extend(["-map", "3:0", "-c:s", "mov_text", "-metadata:s:s:0", "language=por",
                    "-metadata:s:s:0", "title=Português", "-disposition:s:0", "0"])
    mux.extend(["-movflags", "+faststart", "-t", f"{total_duration:.6f}", output])
    ffmpeg(*mux)
    result = probe(output)
    video = next(stream for stream in result["streams"] if stream["codec_type"] == "video")
    if (video["width"], video["height"]) != (1920, 1080):
        raise ValueError("Resolução inesperada no vídeo final.")
    if abs(float(result["format"]["duration"]) - total_duration) > 0.1:
        raise ValueError("A duração do vídeo diverge da narração.")
    ffmpeg("-i", output, "-f", "null", "-")
    report = {"output": str(output.relative_to(ROOT)), "duration": total_duration,
              "video": {"codec": video["codec_name"], "width": video["width"], "height": video["height"],
                        "fps": video["avg_frame_rate"]}, "sources": audit,
              "visual_events": len(events), "chapters": len(chapters), "full_decode": "ok"}
    (build / "verificacao.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
