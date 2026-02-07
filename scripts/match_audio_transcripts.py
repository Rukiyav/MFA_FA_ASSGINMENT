import os
import shutil

# transcript -> audio file mapping
MAPPING = {
    'P1.TXT': 'P1.wav',
    'P2.TXT': 'P2.wav',
    'P3.TXT': 'P3.wav',
    'single_st1.txt': 'single_st1.wav',
    'single_st2.txt': 'single_st2.wav',
    'single_st3.txt': 'single_st3.wav',
}


def match_and_copy(normalized_dir, audio_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    matched = 0
    for txt_name, wav_name in MAPPING.items():
        txt_path = os.path.join(normalized_dir, txt_name)
        wav_path = os.path.join(audio_dir, wav_name)

        if not os.path.exists(txt_path):
            print("  skipping", txt_name, "- transcript not found")
            continue
        if not os.path.exists(wav_path):
            print("  skipping", wav_name, "- audio not found")
            continue

        base = os.path.splitext(txt_name)[0]
        ext = os.path.splitext(wav_name)[1]

        shutil.copy2(txt_path, os.path.join(output_dir, txt_name))
        shutil.copy2(wav_path, os.path.join(output_dir, base + ext))
        matched += 1
        print("  matched", txt_name, "with", wav_name)

    print(matched, "pairs copied to", output_dir)


def update_text_files(normalized_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    count = 0
    for f in sorted(os.listdir(normalized_dir)):
        if f.endswith('.txt') or f.endswith('.TXT'):
            shutil.copy2(
                os.path.join(normalized_dir, f),
                os.path.join(output_dir, f)
            )
            count += 1
            print("  updated", f)

    print(count, "text files refreshed")


def main():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    normalized_dir = os.path.join(project_dir, 'normalized_transcripts')
    audio_dir = os.path.join(project_dir, 'data', 'audio_and_transcripts')
    output_dir = os.path.join(project_dir, 'matched_audio_transcripts')

    if not os.path.exists(normalized_dir):
        print("normalized_transcripts dir not found")
        return
    if not os.path.exists(audio_dir):
        print("audio dir not found:", audio_dir)
        return

    if os.path.exists(output_dir) and os.listdir(output_dir):
        print("already have matched files, just updating transcripts...")
        update_text_files(normalized_dir, output_dir)
    else:
        print("matching audio with transcripts...")
        match_and_copy(normalized_dir, audio_dir, output_dir)


if __name__ == '__main__':
    main()
