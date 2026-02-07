import os
import sys
import shutil

try:
    import soundfile as sf
    import numpy as np
    from scipy import signal
except ImportError:
    print("need soundfile, numpy, scipy - pip install them")
    sys.exit(1)

TARGET_SR = 16000


def check_audio(path):
    try:
        data, sr = sf.read(path)
        channels = 1 if len(data.shape) == 1 else data.shape[1]
        return sr, channels
    except Exception as e:
        print("  couldnt read", path, "-", e)
        return None, None


def convert(audio_path, target_sr=TARGET_SR):
    data, sr = sf.read(audio_path)
    changed = False

    if len(data.shape) > 1:
        data = np.mean(data, axis=1)
        print("    -> mono")
        changed = True

    if sr != target_sr:
        num_samples = int(len(data) * target_sr / sr)
        data = signal.resample(data, num_samples)
        print("    ->", target_sr, "Hz")
        changed = True

    if changed:
        data = data.astype(np.float32)
        sf.write(audio_path, data, target_sr, format='WAV', subtype='PCM_16')

    return changed


def main():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    audio_dir = os.path.join(project_dir, 'matched_audio_transcripts')

    if not os.path.exists(audio_dir):
        print("cant find", audio_dir)
        return

    wav_files = [f for f in os.listdir(audio_dir) if f.lower().endswith('.wav')]
    if not wav_files:
        print("no wav files found")
        return

    print("checking", len(wav_files), "audio files (need 16kHz mono WAV)")

    converted = 0
    for fname in sorted(wav_files):
        path = os.path.join(audio_dir, fname)
        sr, ch = check_audio(path)
        if sr is None:
            continue

        if sr != TARGET_SR or ch != 1:
            print(fname, "- needs conversion (" + str(sr) + "Hz," , str(ch) + "ch)")
            backup = path + '.backup'
            if not os.path.exists(backup):
                shutil.copy2(path, backup)
            convert(path)
            converted += 1
        else:
            print(fname, "- already good")

    print("\ndone,", converted, "converted")


if __name__ == '__main__':
    main()
