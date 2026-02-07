import os
import subprocess
import sys
import tempfile


def get_oov_from_transcripts(directory):
    # find dictionary
    dict_path = None
    for p in [
        os.path.expanduser('~/Documents/MFA/pretrained_models/dictionary/english_us_arpa.dict'),
        os.path.expanduser('~/.local/share/mfa/models/dictionary/english_us_arpa.dict'),
    ]:
        if os.path.exists(p):
            dict_path = p
            break

    if not dict_path:
        print("cant find MFA dictionary")
        return []

    dict_words = set()
    with open(dict_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.split()
            if parts:
                dict_words.add(parts[0].upper())

    oov = set()
    for fname in os.listdir(directory):
        if fname.endswith('.txt') or fname.endswith('.TXT'):
            with open(os.path.join(directory, fname), 'r', encoding='utf-8') as f:
                for word in f.read().strip().upper().split():
                    if word not in dict_words:
                        oov.add(word)

    return sorted(oov)


def try_g2p(words):
    # find g2p model
    g2p_path = None
    for p in [
        os.path.expanduser('~/Documents/MFA/pretrained_models/g2p/english_us_arpa.zip'),
        os.path.expanduser('~/.local/share/mfa/models/g2p/english_us_arpa.zip'),
    ]:
        if os.path.exists(p):
            g2p_path = p
            break

    if not g2p_path:
        print("g2p model not found, download it with mfa model download g2p english_us_arpa")
        return {}

    input_f = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    for w in words:
        input_f.write(w + '\n')
    input_f.close()

    output_f = tempfile.NamedTemporaryFile(suffix='.dict', delete=False)
    output_f.close()

    pronunciations = {}
    try:
        result = subprocess.run(
            ['mfa', 'g2p', '--overwrite', input_f.name, 'english_us_arpa', output_f.name],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and os.path.getsize(output_f.name) > 0:
            with open(output_f.name, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        pronunciations[parts[0].upper()] = ' '.join(parts[1:])
    except Exception as e:
        print("g2p didnt work:", e)
    finally:
        os.unlink(input_f.name)
        try:
            os.unlink(output_f.name)
        except:
            pass

    return pronunciations


def main():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    matched_dir = os.path.join(project_dir, 'matched_audio_transcripts')

    print("looking for OOV words...")
    oov_words = get_oov_from_transcripts(matched_dir)

    if not oov_words:
        print("no OOV words, everything is in the dictionary")
        return

    print("found", len(oov_words), "OOV words:", ", ".join(oov_words))

    print("\ntrying automatic g2p...")
    pronunciations = try_g2p(oov_words)

    if pronunciations:
        print("\ngot these pronunciations:")
        for word, pron in sorted(pronunciations.items()):
            print("  " + word + "\t" + pron)
    else:
        print("\nautomatic g2p didnt work")
        print("add pronunciations manually to custom_dictionary.txt")
        print("format (tab separated):")
        print("  DUKAKIS\tD UW0 K AA1 K IH0 S")
        print("  WBUR\tW AH1 B ER0")
        print("then run merge_dictionary.py to merge with base dictionary")


if __name__ == '__main__':
    main()
