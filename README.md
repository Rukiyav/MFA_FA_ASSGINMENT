# Forced-Alignment-using-Montreal-Forced-Aligner-MFA


## Project Overview

This project implements a complete workflow for forced alignment of audio and transcript files using Montreal Forced Alignment (MFA). The workflow includes transcript normalization, audio format conversion, pre-validation checks, Out-of-Vocabulary (OOV) word handling, and final alignment generation.

## Prerequisites

- **Operating System**: macOS, Linux, or Windows
- **Python**: 3.8 or higher
- **Conda**: For managing MFA environment
- **MFA Models**: English US ARPA acoustic and dictionary models

## Installation

### 1. Create MFA Conda Environment

```bash
conda create -n mfa -c conda-forge montreal-forced-alignment
conda activate mfa
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `num2words>=0.5.6` - For number to word conversion
- `nltk>=3.8` - For text tokenization and processing
- `soundfile>=0.12.1` - For audio format conversion
- `numpy>=1.24.0` - For audio processing
- `scipy>=1.10.0` - For audio resampling

### 3. Download MFA Models

```bash
mfa model download acoustic english_us_arpa
mfa model download dictionary english_us_arpa
```

## Workflow Steps

### Step 1: Normalize Transcripts

Normalize transcript files to MFA-compatible format (uppercase, no punctuation, numbers as words).

```bash
python scripts/normalize_transcripts.py
```

**What it does:**
- Removes punctuation and replaces with spaces
- Converts numbers to words (e.g., "1971" → "NINETEEN SEVENTY ONE")
- Expands abbreviations (e.g., "S.J.C." → "S J C")
- Expands possessives (e.g., "WBUR's" → "WBUR S")
- Handles hyphens (e.g., "de-politicize" → "DE POLITICIZE")
- Converts to uppercase
- Ensures single-line format

**Input:** `input_files/audio_and_transcripts/*.txt`  
**Output:** `normalized_transcripts/*.txt`

### Step 2: Match Audio with Transcripts

Match normalized transcripts with corresponding audio files and organize them into a single directory.

```bash
python scripts/match_audio_transcripts.py
```

**What it does:**
- Maps transcript names to audio file names
- Copies matched pairs to `matched_audio_transcripts/` directory
- Renames audio files to match transcript names

**Input:** 
- `normalized_transcripts/*.txt`
- `original/wav/*.wav`

**Output:** `matched_audio_transcripts/` (contains both .txt and .wav files)

### Step 3: Convert Audio to MFA Requirements

Ensure audio files meet MFA format requirements (16kHz, mono, WAV PCM).

```bash
python scripts/convert_audio_for_mfa.py
```

**MFA Audio Requirements:**
- **Format**: .wav (PCM)
- **Sampling Rate**: 16,000 Hz (16kHz)
- **Channels**: Mono (single channel)

**What it does:**
- Checks current audio properties
- Converts stereo to mono (averages channels)
- Resamples to 16kHz if needed
- Saves as WAV PCM format
- Creates backup files before conversion

**Input:** `matched_audio_transcripts/*.wav`  
**Output:** `matched_audio_transcripts/*.wav` (converted in-place with backups)

### Step 4: Pre-Validation Check

Validate audio-transcript pairs before alignment to identify potential issues.

```bash
python scripts/validate_for_mfa.py
```

**What it checks:**
1. **Duration Matching**: Compares audio duration with estimated speech duration
2. **Out of Vocabulary (OOV) Words**: Identifies words not in the MFA dictionary

**Output:** Validation report printed to console and saved to `validation_report.txt`

### Step 5: Create Merged Dictionary

Merge custom OOV words with the base MFA dictionary.

```bash
python scripts/merge_dictionary.py
```

**What it does:**
- Locates the base MFA dictionary (`english_us_arpa.dict`) on your system
- Reads the custom OOV word entries from `custom_dictionary.txt`
- Merges both dictionaries (custom entries override base entries)
- Writes the combined dictionary to `merged_dictionary.dict`

The custom dictionary (`custom_dictionary.txt`) contains 5 OOV words:
- DUKAKIS
- MAFFY
- MELNICOVE
- POLITICIZE
- WBUR

**Input:** `custom_dictionary.txt`  
**Output:** `merged_dictionary.dict`

### Step 6: Run MFA Alignment

Perform forced alignment using the merged dictionary.

```bash
mfa align matched_audio_transcripts merged_dictionary.dict english_us_arpa outputs --clean
```

**Parameters:**
- `matched_audio_transcripts` - Input directory with audio and transcript pairs
- `merged_dictionary.dict` - Merged dictionary (base + OOV words)
- `english_us_arpa` - Acoustic model
- `outputs` - Output directory for TextGrid files
- `--clean` - Clears cached results from previous runs

**Output:** 
- TextGrid files in `outputs/` directory
- `alignment_analysis.csv` with alignment quality metrics


## Troubleshooting

### Issue: MFA command not found
**Solution:** Ensure the `mfa` conda environment is activated:
```bash
conda activate mfa
```

### Issue: ModuleNotFoundError for Python packages
**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: Audio files not in correct format
**Solution:** Run the audio conversion script:
```bash
python scripts/convert_audio_for_mfa.py
```

### Issue: OOV words showing as "spn" (spoken noise) tags
**Solution:** 
1. Ensure custom dictionary entries are in uppercase
2. Create merged dictionary (Step 5)
3. Use merged dictionary in alignment command
4. Use `--clean` flag to clear cached results

### Issue: Duration mismatches in validation
**Solution:** 
- Check that transcript text matches what's spoken in audio
- Verify audio files are complete and not truncated
- Some mismatch is acceptable (within 20% tolerance)

### Issue: Transcript normalization issues
**Solution:**
- Check that input files are in `input_files/audio_and_transcripts/`
- Verify file encoding is UTF-8
- Review normalization script output for errors

## Results

After successful alignment:
- All 6 audio-transcript pairs aligned
- 5 OOV words successfully handled (100% resolution rate)
- 0 "spn" tags in final output
- Proper ARPABET phoneme alignments for all words

## References

- [Montreal Forced Aligner Documentation](https://montreal-forced-aligner.readthedocs.io/)
- [MFA GitHub Repository](https://github.com/MontrealCorpusTools/Montreal-Forced-Alignment)

## License

This project is part of IIIT Hyderabad  assignment.

