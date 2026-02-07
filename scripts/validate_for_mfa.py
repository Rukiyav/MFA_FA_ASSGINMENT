import os
import sys

try:
    import soundfile as sf
except ImportError:
    print("need soundfile: pip install soundfile")
    sys.exit(1)

WORDS_PER_MIN = 150


def get_duration(audio_path):
    try:
        data, sr = sf.read(audio_path)
        return len(data) / sr
    except:
        return None


def load_dictionary(dict_path):
    words = set()
    if dict_path and os.path.exists(dict_path):
        with open(dict_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.split()
                if parts:
                    words.add(parts[0].upper())
    return words


def validate(directory, dict_path=None):
    transcripts = sorted([
        f for f in os.listdir(directory)
        if f.endswith('.txt') or f.endswith('.TXT')
    ])

    if not transcripts:
        print("no transcripts found")
        return

    dict_words = load_dictionary(dict_path)
    if dict_words:
        print("dictionary loaded,", len(dict_words), "words")

    all_oov = set()
    duration_issues = []

    for txt_file in transcripts:
        base = os.path.splitext(txt_file)[0]
        wav_file = base + '.wav'
        txt_path = os.path.join(directory, txt_file)
        wav_path = os.path.join(directory, wav_file)

        print("\n---", txt_file, "/", wav_file, "---")

        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        words = text.upper().split()
        unique_words = sorted(set(words))

        # check duration
        if os.path.exists(wav_path):
            dur = get_duration(wav_path)
            if dur:
                est = (len(words) / WORDS_PER_MIN) * 60
                diff = abs(dur - est)
                pct = (diff / est * 100) if est > 0 else 0
                print("  audio:", round(dur, 1), "s, estimated:", round(est, 1), "s (" + str(len(words)), "words)")
                if pct > 20:
                    print("  ^ big difference:", round(pct), "%")
                    duration_issues.append(txt_file)
        else:
            print("  no audio file found")

        # check OOV
        if dict_words:
            oov = [w for w in unique_words if w not in dict_words]
            if oov:
                print("  OOV words:", ", ".join(oov))
                all_oov.update(oov)
            else:
                print("  no OOV words")

    # print summary
    print("\n--- summary ---")
    print("checked", len(transcripts), "files")
    if duration_issues:
        print("duration issues in:", ", ".join(duration_issues))
    if all_oov:
        print("all OOV words:", ", ".join(sorted(all_oov)))
        print("these need to go in the dictionary")


def main():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    directory = os.path.join(project_dir, 'matched_audio_transcripts')

    dict_path = None
    for p in [
        os.path.expanduser('~/Documents/MFA/pretrained_models/dictionary/english_us_arpa.dict'),
        os.path.expanduser('~/.local/share/mfa/models/dictionary/english_us_arpa.dict'),
    ]:
        if os.path.exists(p):
            dict_path = p
            break

    if dict_path:
        print("using dictionary:", dict_path)

    validate(directory, dict_path)


if __name__ == '__main__':
    main()
