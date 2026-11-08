"""Generate three Jupyter notebooks using only the Python standard library."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notebooks"


def code(source):
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": (source.strip() + "\n").splitlines(keepends=True)}


def md(source):
    return {"cell_type": "markdown", "metadata": {},
            "source": (source.strip() + "\n").splitlines(keepends=True)}


def save(name, cells):
    OUT.mkdir(parents=True, exist_ok=True)
    notebook = {
        "cells": cells,
        "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                     "language_info": {"name": "python"}},
        "nbformat": 4, "nbformat_minor": 4
    }
    (OUT / name).write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Built", name, "with", len(cells), "cells")


SETUP = """from pathlib import Path
import json, re, statistics
from collections import Counter
import pandas as pd

ROOT = Path.cwd()
if not (ROOT / "corpus").exists():
    ROOT = ROOT.parent
assert (ROOT / "corpus").exists(), "Run notebook from UniAssist_UMT directory"
metadata = json.loads((ROOT / "metadata.json").read_text(encoding="utf-8"))
records = metadata["documents"]
texts = [(ROOT / "corpus" / row["file"]).read_text(encoding="utf-8") for row in records]
print(len(texts), "documents loaded")
"""


def notebook1():
    return [
        md("""# UniAssist — Week 1: Corpus and Textual Sources
The corpus contains 20 English source-based texts about University Metropolitan Tirana (UMT).
The source metadata records URLs and flags time-sensitive policies.
Complete the discussion questions after running the cells; generated counts are not manual gold judgments."""),
        code(SETUP),
        md("## Task 1 — Inventory, word counts, source genres and quality"),
        code("""rows = []
for entry, text in zip(records, texts):
    rows.append({"filename": entry["file"], "genre": entry["genre"],
                 "chars": len(text), "whitespace_tokens": len(text.split()),
                 "source_count": len(entry["sources"]),
                 "time_sensitive": entry["time_sensitive"]})
table = pd.DataFrame(rows)
display(table)
print("Total words:", table["whitespace_tokens"].sum())
print("Genres:", table["genre"].value_counts().to_dict())
print("Exact duplicate texts:", len(texts)-len(set(texts)))
"""),
        md("## Task 2 — Tokens, types and common words using spaCy"),
        code("""import spacy
nlp = spacy.blank("en")
all_tokens = [tok.text.lower() for text in texts for tok in nlp.make_doc(text) if not tok.is_space]
alpha = [tok for tok in all_tokens if tok.isalpha()]
print("Alphabetic tokens:", len(alpha), "types:", len(set(alpha)))
print("Type/token ratio:", round(len(set(alpha)) / max(1, len(alpha)), 4))
print("Top 15:", Counter(alpha).most_common(15))
filtered = [tok for tok in alpha if tok not in nlp.Defaults.stop_words]
print("Top 15 without stopwords:", Counter(filtered).most_common(15))
"""),
        md("## Task 3 — UTF-8, punctuation and difficult text"),
        code("""print("All files decoded as UTF-8")
for row, text in zip(records, texts):
    if re.search(r"[À-ÿ–—+]", text):
        print(row["file"], "has accents or special symbols")
print("Potential replacement characters:", sum(text.count("�") for text in texts))
"""),
        md("""## Task 4 — Dependency parsing and named entities
Install the model with: python -m spacy download en_core_web_sm.
Mark at least one correct and one incorrect result for each of three sentences."""),
        code("""from spacy import displacy
try:
    trained = spacy.load("en_core_web_sm")
except OSError:
    print("Install en_core_web_sm to enable dependency and entity visualization.")
else:
    examples = [
        "University Metropolitan Tirana has a Faculty of Computer Science and IT.",
        "The university's English admissions page discusses State Matura.",
        "Erasmus+ students may need a Learning Agreement."
    ]
    for sentence in examples:
        doc = trained(sentence)
        print(sentence, [(e.text, e.label_) for e in doc.ents])
        from IPython.display import HTML
        display(HTML(displacy.render(doc, style="dep", jupyter=False)))
        display(HTML(displacy.render(doc, style="ent", jupyter=False)))
"""),
        md("""## Submit
1. Three sentences describing the corpus, its source and its genres.
2. Corpus statistics and 10 most frequent words.
3. Three analyzed sentences with one correct and one incorrect NLP annotation each.
4. Source list and copyright/permission notes; explain why outdated rules are flagged.""")
    ]


def notebook2():
    return [
        md("""# UniAssist — Week 2: Tokenization, Sentence Boundaries and Subwords
Compare whitespace, NLTK and spaCy on the original corpus. Complete manual tokenization before judging which tokenizer is best."""),
        code(SETUP),
        code("""import nltk, spacy
from nltk.tokenize import word_tokenize, sent_tokenize
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nlp = spacy.blank("en")
nlp.add_pipe("sentencizer")
methods = {
    "split": lambda t: t.split(),
    "nltk": lambda t: word_tokenize(t, preserve_line=True),
    "spaCy": lambda t: [w.text for w in nlp.make_doc(t) if not w.is_space],
}
"""),
        md("## Task A — Token/type counts and type-token ratios"),
        code("""rows = []
for name, fn in methods.items():
    toks = [word for text in texts for word in fn(text)]
    types = len(set(w.lower() for w in toks))
    punct = sum(not any(ch.isalnum() for ch in word) for word in toks)
    rows.append({"Tokenizer": name, "Tokens": len(toks), "Types": types,
                 "Types/Tokens": round(types / max(1, len(toks)), 4),
                 "Punct. tokens": punct})
display(pd.DataFrame(rows))
"""),
        md("## Task B — Regex problem hunt: URLs, emails, dates and punctuation"),
        code(r"""patterns = {
    "url": r"https?://\S+|www\.\S+",
    "email": r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+",
    "number": r"\d[\d.,:/-]*\d|\d",
    "hyphenated": r"\w+(?:-\w+)+",
    "apostrophe": r"\w+['’]\w+",
    "abbreviation": r"\b[A-Z][a-z]{0,3}\.",
    "other_symbol": r"[^\w\s.,;:!?()'\-]"
}
found_rows = []
for kind, pattern in patterns.items():
    matches = [(record["file"], m.group()) for record, text in zip(records, texts)
               for m in re.finditer(pattern, text)]
    found_rows.append({"type": kind, "number": len(matches), "three_examples": matches[:3]})
display(pd.DataFrame(found_rows))
"""),
        md("## Task C — Compare the same five tricky expressions across tokenizers"),
        code("""hard = ["2026–2027", "Erasmus+", "Engineer-Architect",
        "State Matura", "https://umt.edu.al/en/admissions/"]
for sample in hard:
    print("\\nEXPRESSION:", sample)
    for name, tokenize in methods.items():
        print(name, len(tokenize(sample)), tokenize(sample))
"""),
        md("## Task D — Sentence segmentation and mean/median sentence lengths"),
        code("""def spacy_sents(text):
    return [s.text.strip() for s in nlp(text).sents if s.text.strip()]

sentences = [s for text in texts for s in spacy_sents(text)]
lengths = [(len(methods["spaCy"](s)), s) for s in sentences]
nums = [n for n,_ in lengths]
print("Sentences", len(sentences), "Mean", statistics.mean(nums), "Median", statistics.median(nums))
for count, sentence in sorted(lengths, reverse=True)[:5]:
    print(count, sentence[:170])
sample = texts[14]
print("Comparing NLTK and spaCy for one document:")
print("NLTK", len(sent_tokenize(sample)), "spaCy", len(spacy_sents(sample)))
"""),
        md("""## Optional Task E — Subword comparison
If you install transformers and sentencepiece, the following cell downloads model tokenizers. It may require internet access."""),
        code("""try:
    from transformers import AutoTokenizer
except ImportError:
    print("Optional dependency not installed: pip install transformers sentencepiece")
else:
    models = {"BERT":"bert-base-uncased", "GPT-2":"gpt2",
              "XLM-R":"xlm-roberta-base"}
    for name, checkpoint in models.items():
        try:
            tok = AutoTokenizer.from_pretrained(checkpoint)
            print(name, {word:tok.tokenize(word) for word in
                  ("university", "registration", "Erasmus+", "Metropolitan Tirana")})
        except Exception as err:
            print(name, "could not download:", type(err).__name__)
"""),
        md("""## Submit
Show the three tokenization tables, five difficult strings, mean/median sentence lengths, five longest sentences and your explanations. Explicitly distinguish manual decisions from software output.""")
    ]


def notebook3():
    return [
        md("""# UniAssist — Week 3: Morphology, Stemming, Lemmatization and WordNet
Use the original UMT corpus to compare stemming algorithms, POS-aware lemmatization and semantic relations. We evaluate outputs on examples rather than presuming that any single algorithm is correct for every word."""),
        code(SETUP),
        code("""import nltk, spacy
from nltk.stem import PorterStemmer, SnowballStemmer, LancasterStemmer, WordNetLemmatizer
from nltk.corpus import wordnet as wn
from nltk import pos_tag
for dataset in ("wordnet", "omw-1.4", "averaged_perceptron_tagger_eng"):
    nltk.download(dataset, quiet=True)
porter = PorterStemmer()
snowball = SnowballStemmer("english")
lancaster = LancasterStemmer()
lemmatizer = WordNetLemmatizer()
nlp = spacy.blank("en")
"""),
        md("## Task A — Compare three stemmers on vocabulary from UMT documents"),
        code("""words = ["studies", "studying", "universities", "student", "students",
         "admissions", "admitted", "evaluation", "evaluated", "applications",
         "faculties", "scholarships", "architectural", "mobility", "programmes"]
stem_table = pd.DataFrame([{
    "word": word, "Porter": porter.stem(word),
    "Snowball": snowball.stem(word), "Lancaster": lancaster.stem(word)
} for word in words])
display(stem_table)
print("Porter distinct stems:", stem_table["Porter"].nunique())
print("Snowball distinct stems:", stem_table["Snowball"].nunique())
print("Lancaster distinct stems:", stem_table["Lancaster"].nunique())
"""),
        md("""## Task B — Corpus-level vocabulary reduction
Stemming is a string normalization technique, not guaranteed grammatical lemmatization. Compare unique terms only after lowercasing and filtering alphabetic tokens."""),
        code("""words_in_corpus = [token.text.lower() for text in texts
                   for token in nlp.make_doc(text) if token.is_alpha]
rows = []
for name, transform in [("unchanged", lambda s:s), ("Porter", porter.stem),
                        ("Snowball", snowball.stem), ("Lancaster", lancaster.stem)]:
    forms = [transform(word) for word in words_in_corpus]
    rows.append({"method": name, "tokens": len(forms), "types": len(set(forms)),
                 "TTR": round(len(set(forms))/max(1, len(forms)), 4)})
display(pd.DataFrame(rows))
"""),
        md("## Task C — Lemmatization without POS versus POS-aware WordNet lemmatization"),
        code("""def wn_pos(tag):
    # Penn Treebank tag initials: adjective, verb, noun, adverb.
    return {"J":wn.ADJ, "V":wn.VERB, "N":wn.NOUN, "R":wn.ADV}.get(tag[:1], wn.NOUN)

samples = ["Students were studying admission requirements carefully.",
           "The faculties offered different programmes and scholarships.",
           "Visitors asked about better learning facilities and transferred credits."]
lemma_rows = []
for sentence in samples:
    tokens = nltk.word_tokenize(sentence, preserve_line=True)
    tagged = pos_tag(tokens)
    for word, tag in tagged:
        if word.isalpha():
            lemma_rows.append({"sentence": sentence, "word": word, "POS": tag,
                "default_noun": lemmatizer.lemmatize(word.lower()),
                "POS_aware": lemmatizer.lemmatize(word.lower(), wn_pos(tag))})
display(pd.DataFrame(lemma_rows))
"""),
        md("""## Task D — spaCy lemmatization on actual source-based text
This requires the trained English model. Compare it with the WordNet POS-aware results and note errors for UMT proper names, acronyms, and domain vocabulary."""),
        code("""try:
    trained = spacy.load("en_core_web_sm")
except OSError:
    print("Missing spaCy language model. Run: python -m spacy download en_core_web_sm")
else:
    sample_doc = trained(texts[0][:1300])
    display(pd.DataFrame([{"token": tok.text, "lemma": tok.lemma_, "coarse_POS": tok.pos_,
                           "fine_POS": tok.tag_} for tok in sample_doc if tok.is_alpha]).head(55))
"""),
        md("""## Task E — WordNet senses, hypernyms, and semantic similarity
WordNet describes general English, not UMT's internal policies. The first WordNet sense is not automatically the correct sense in a university context."""),
        code("""terms = ["university", "student", "course", "admission", "library", "faculty"]
for term in terms:
    senses = wn.synsets(term, pos=wn.NOUN)
    print("\\n", term, "senses:", len(senses))
    for syn in senses[:2]:
        print(" ", syn.name(), "-", syn.definition())
        print("   hypernyms:", [h.name() for h in syn.hypernyms()[:3]])

pairs = [("student", "scholar"), ("university", "college"),
         ("course", "class"), ("library", "school")]
for left, right in pairs:
    a = wn.synsets(left, pos=wn.NOUN)
    b = wn.synsets(right, pos=wn.NOUN)
    value = a[0].wup_similarity(b[0]) if a and b else None
    print(left, right, "first-sense Wu-Palmer similarity:", value)
"""),
        md("## Task F — Error analysis and implications for search"),
        code("""examples = ["studies", "universities", "admission", "programmes",
            "Erasmus", "UMT", "better", "running", "architecture"]
display(pd.DataFrame([{"input": w, "Porter": porter.stem(w),
                       "Snowball": snowball.stem(w),
                       "noun_lemma": lemmatizer.lemmatize(w.lower())} for w in examples]))
"""),
        md("""## Submit
1. Compare 15 words across Porter, Snowball and Lancaster.
2. Explain observed vocabulary reduction and at least three overstemming/understemming cases.
3. Contrast default WordNet, POS-aware WordNet and spaCy lemmas with examples.
4. Display at least six WordNet lookup results and four semantic comparisons.
5. State which normalization you would use for the eventual TF-IDF search and why, including limitations.""")
    ]


if __name__ == "__main__":
    save("01_corpus_overview.ipynb", notebook1())
    save("02_tokenization_sentences.ipynb", notebook2())
    save("03_stemming_lemmatization_wordnet.ipynb", notebook3())
