import os
import sys

# Merge the custom OOV pronunciations with the base MFA dictionary
# so that MFA can align words like DUKAKIS, WBUR etc.

def main():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    custom_dict_path = os.path.join(project_dir, 'custom_dictionary.txt')
    output_path = os.path.join(project_dir, 'merged_dictionary.dict')

    # find the base dictionary
    base_dict_path = None
    for p in [
        os.path.expanduser('~/Documents/MFA/pretrained_models/dictionary/english_us_arpa.dict'),
        os.path.expanduser('~/.mfa/pretrained_models/dictionary/english_us_arpa.dict'),
    ]:
        if os.path.exists(p):
            base_dict_path = p
            break

    if not base_dict_path:
        print("cant find english_us_arpa.dict, download it first")
        sys.exit(1)

    if not os.path.exists(custom_dict_path):
        print("custom_dictionary.txt not found")
        sys.exit(1)

    # read base dictionary
    base_words = {}
    with open(base_dict_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                base_words[parts[0].strip().upper()] = line.strip()

    print("base dictionary:", len(base_words), "words")

    # read and add custom OOV entries
    custom_count = 0
    with open(custom_dict_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split('\t')
            if len(parts) >= 2:
                word = parts[0].strip().upper()
                pron = parts[1].strip()
                base_words[word] = word + "\t" + pron
                custom_count += 1
                print("  adding", word)

    # write it out
    with open(output_path, 'w', encoding='utf-8') as f:
        for word in sorted(base_words.keys()):
            f.write(base_words[word] + '\n')

    print("merged", custom_count, "custom words, total", len(base_words))
    print("saved to", output_path)


if __name__ == '__main__':
    main()
