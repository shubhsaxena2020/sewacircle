# Name gazetteers (used only to mask person names before text is sent to a language model)

`indian_names_merged.txt` (used by `app/llm/names.py`, 61,113 entries) merges three Kaggle datasets, downloaded 2026-11-19:
1. "Indian Names Corpus (nltk_data)", manojmaharana - https://www.kaggle.com/datasets/manojmaharana/indian-names-corpus-nltk-data - licence on Kaggle: MIT.
2. "Indian Names Dataset", ananysharma - https://www.kaggle.com/datasets/ananysharma/indian-names-dataset - licence on Kaggle: unknown.
3. "Indian Names for new first name generation", suryasiriki1 - https://www.kaggle.com/datasets/suryasiriki1/indian-names-for-new-first-name-generation - licence on Kaggle: unknown.
Sources 2 and 3 have no stated licence; the owner chose to use them for their larger volume. Only bare name tokens are kept
(a list of first names and surnames, no other fields). Remove them before any commercial use until the licence is clarified.

Processing: split multi-word entries, keep alphabetic tokens of length >= 3, Title Case, de-duplicate; remove words that also
appear as ordinary lower-case words in this project's own documents and code (161 words such as Any, Data, Date, Driver, One),
UP district/block names and domain words (Asha, Seva, Bharat, Hindi ...); then re-add 19 common surnames/names removed by that
heuristic (Mohit, Rahul, Sharma, Verma, Singh ...).
Measured (tests/llm/test_names.py and the head's check, 2026-11-19): 0 masks on the 30 extraction-eval briefs and on the
10 synthetic task briefs/titles/places; 38/40 synthetic first names caught (misses: "Asha" by design, "Om" too short).
Limit: Latin script only. Devanagari names are not masked.

`indian_names_mit.txt` is the smaller MIT-only list (3,127 entries) kept for reference.
