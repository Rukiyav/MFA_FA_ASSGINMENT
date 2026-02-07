import os
import re
import glob
import nltk
from num2words import num2words

# make sure punkt tokenizer is there
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)


def expand_numbers(text):
    """Convert numbers to words. Years like 1971 get split: nineteen seventy one"""
    def number_to_words(match):
        num_str = match.group(0)
        try:
            if len(num_str) == 4 and num_str.isdigit():
                year = int(num_str)
                if 1000 <= year <= 2099:
                    first = year // 100
                    second = year % 100
                    if second == 0:
                        words = num2words(first) + " hundred"
                    else:
                        first_w = num2words(first).replace('-', ' ')
                        second_w = num2words(second).replace('-', ' ')
                        words = first_w + " " + second_w
                else:
                    words = num2words(year).replace('-', ' ')
            else:
                words = num2words(int(num_str)).replace('-', ' ')
            return words.upper()
        except:
            return num_str

    return re.sub(r'\b\d+\b', number_to_words, text)


def expand_abbreviations(text):
    """S.J.C. -> S J C"""
    pattern = r'\b([A-Za-z]\.)+[A-Za-z]\.?(?:\'s)?'
    def expand(match):
        letters = re.findall(r'[A-Za-z]', match.group(0))
        return ' '.join(letters)
    return re.sub(pattern, expand, text)


def expand_possessives(text):
    """WBUR's -> WBUR S"""
    return re.sub(r"\b([A-Za-z0-9]+)'s\b", r'\1 S', text)


def remove_punctuation(text):
    tokens = nltk.word_tokenize(text)
    words = [t for t in tokens if t.isalnum() or any(c.isdigit() for c in t)]
    return ' '.join(words)


def normalize_text(text):
    text = ' '.join(text.splitlines())

    # deal with hyphens first
    text = re.sub(r'\s*-\s+', ' ', text)
    text = re.sub(r'\s+-\s*', ' ', text)
    text = re.sub(r'([A-Za-z0-9])-([A-Za-z0-9])', r'\1 \2', text)

    text = expand_possessives(text)
    text = expand_abbreviations(text)
    text = expand_numbers(text)
    text = remove_punctuation(text)
    text = text.upper()
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def process_transcripts(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    txt_files = glob.glob(os.path.join(input_dir, '*.txt'))
    txt_files.extend(glob.glob(os.path.join(input_dir, '*.TXT')))
    txt_files = list(set(txt_files))

    if not txt_files:
        print("no text files in", input_dir)
        return

    print("processing", len(txt_files), "files")

    for txt_file in sorted(txt_files):
        with open(txt_file, 'r', encoding='utf-8') as f:
            original = f.read()

        normalized = normalize_text(original)
        filename = os.path.basename(txt_file)
        out_path = os.path.join(output_dir, filename)

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(normalized)

        print("  done:", filename)

    print("output in", output_dir)


def main():
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_dir = os.path.join(script_dir, 'data', 'audio_and_transcripts')
    output_dir = os.path.join(script_dir, 'normalized_transcripts')

    if not os.path.exists(input_dir):
        print("input dir not found:", input_dir)
        return

    process_transcripts(input_dir, output_dir)


if __name__ == '__main__':
    main()
