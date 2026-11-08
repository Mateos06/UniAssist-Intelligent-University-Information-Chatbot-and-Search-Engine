# Final project proposal: UniAssist — Intelligent University Information Assistant

**Case study:** Metropolitan University of Tirana (UMT)  
**Language:** English  
**Course:** Natural Language Processing (NLP)  
**Current delivery:** corpus development and exercises aligned with Weeks 1–3  
**Future product:** a document-grounded university search engine, autocomplete and simple chatbot

## 1. Problem and purpose

A prospective or current student may need information about study programmes, admissions, scholarship opportunities, Erasmus mobility, campus services or where to find an applicable examination regulation. Relevant information is distributed across university webpages, PDFs and announcements, and a user may describe their need in natural language rather than by an exact document title.

**UniAssist** is a course project that will investigate how basic NLP processing can organize these texts and support accurate information retrieval. The final prototype should accept questions such as “Where do I find bachelor admission guidance?”, “Does UMT describe Erasmus mobility?”, or “What information is available about laboratories?” It should link back to the official source rather than invent an academic rule.

Research questions:

1. What differences arise when whitespace, NLTK and spaCy tokenize university-oriented English text?
2. How do stemming and POS-aware lemmatization change vocabulary size and normalize variant forms?
3. Which terms or entities cause errors, such as “Erasmus+”, “ECTS”, programme names and year ranges?
4. Later, how well can a small 20-document corpus retrieve the correct source for a natural-language question, and when should the assistant abstain?

## 2. Corpus design

Target **20 independent `.txt` files**, each **200–300 words**, encoded as **UTF-8**, for roughly **4,000–6,000 words**. Each file has a descriptive filename, title, one text type and attribution metadata. Three genres provide variation: 9 `information_article`, 6 `visitor_faq`, and 5 `policy_summary`. Some materials are institutional webpages; the policy texts are explanatory English summaries of dated university-source documents, not invented regulations or verbatim translations.

This mixed-genre approach must be approved by the lecturer if the original exercise requires a single genre. It can be adapted to one genre without changing the underlying source set.

### Source plan for exactly 20 documents

| ID | Topic / output file | Genre | Official UMT source(s) | Important verification note |
|---|---|---|---|---|
| 01 | `01_university_overview.txt` | Information | Faculties; facilities | Organizational overview |
| 02 | `02_computer_science_faculty.txt` | Information | Faculty of Computer Science & IT | Programme lists can change |
| 03 | `03_engineering_architecture_faculty.txt` | Information | Faculty of Engineering & Architecture | Programme lists can change |
| 04 | `04_economics_faculty.txt` | Information | Faculty of Economics | Programme lists can change |
| 05 | `05_english_taught_programs.txt` | Information | Study programmes for international students | Teaching language and programmes require recheck |
| 06 | `06_bachelor_admissions_faq.txt` | FAQ | Admissions; 2026–27 admission decision | No guarantee of admission or current opening |
| 07 | `07_bachelor_documents_faq.txt` | FAQ | Admissions; international students | Requirements may vary by applicant |
| 08 | `08_master_admissions_faq.txt` | FAQ | Admissions | Entry criteria depend on current programme |
| 09 | `09_professional_doctoral_studies.txt` | Information | Admissions; CS/IT faculty | Availability is year-specific |
| 10 | `10_scholarships_faq.txt` | FAQ | Study scholarships | No promised eligibility or awards |
| 11 | `11_study_fees_student_access_faq.txt` | FAQ | Study fees; admissions | No unsupported fee amounts |
| 12 | `12_academic_calendar_2026_2027.txt` | Policy source summary | 2026–27 calendar PDF; announcements | Albanian PDF; exact dates deliberately omitted |
| 13 | `13_degree_duration_ects.txt` | Policy source summary | Admissions | Degree/ECTS descriptions are page-based |
| 14 | `14_examination_regulation_scope.txt` | Policy source summary | Examination regulation PDF | Published under 2022 path; current version unconfirmed |
| 15 | `15_grading_documentation.txt` | Policy source summary | Examination regulation PDF | Historical document warning required |
| 16 | `16_transfer_of_studies_faq.txt` | FAQ | Transfer of studies | Personal eligibility needs official assessment |
| 17 | `17_dean_of_students_support.txt` | Information | Dean of Students | Describes available contact channel |
| 18 | `18_careers_clubs_student_life.txt` | Information | Dean of Students; student life | Activities change by semester |
| 19 | `19_campus_laboratories_library.txt` | Information | Facilities and laboratories | Describes published physical resources |
| 20 | `20_erasmus_mobility_information.txt` | Policy source summary | Outgoing; incoming; Erasmus | Individual calls and conditions change |

Every specific URL, word count, source language, document genre and time-sensitivity flag is recorded in `metadata.json`. The deduplicated source manifest is `sources.json`. Reference URLs in text files serve provenance, while the structured records support citation display in a later chatbot.

## 3. Methods: work performed in Weeks 1–3

### Week 1 — Introduction, corpus and textual sources

- Justify topic, representative text selection, genre diversity and language.
- Read every UTF-8 file, calculate documents, words, characters and duplicates.
- Extract token frequencies, remove stopwords and compare types versus tokens.
- Demonstrate dependency parsing and named entity recognition (NER) on selected university sentences with spaCy.
- Discuss source attribution, copyright, date sensitivity and named-entity errors.

### Week 2 — Tokenization and sentence segmentation

- Implement whitespace splitting, NLTK tokenization and spaCy tokenization.
- Compare corpus-wide token counts, type counts and type-token ratios (TTR).
- Identify tricky expressions: URLs, hyphenation, apostrophes, numbers, “Erasmus+” and academic years.
- Segment sentences and compute length distribution, mean, median and outliers.
- Optionally examine model subwords using Hugging Face tokenizers (requires optional installation and internet).

### Week 3 — Morphology and lexical semantics

- Compare Porter, Snowball and Lancaster stems for academic terms.
- Measure vocabulary reduction and identify possible over/understemming.
- Compare WordNet default lemmatization with POS-aware forms and spaCy trained lemmas.
- Explore WordNet senses, definitions, hypernyms and similarity, noting that domain meanings can be mismatched.
- Decide which text normalization to try later during retrieval.

## 4. Later architecture

```text
Official UMT webpages/PDFs
            |
Source metadata + 20 UTF-8 text summaries
            |
Validation → tokenizer → optional normalization
            |
TF–IDF/BM25 search index
            |
  +---------+-----------+
  |                     |
Autocomplete       Query retrieval
                        |
             Retrieved snippet + source link
                        |
              Grounded FAQ/chat interface
```

Start with traditional NLP and information retrieval so the method is understandable and evaluable; a large language model is not required to satisfy the early coursework. A generative interface could be explored later only with retrieval-based citation and abstention safeguards.

## 5. Evaluation plan

Create a small annotated set of ~30 natural-language user queries spanning programme information, admissions, services, mobility and deliberately unanswerable questions. Mark relevant document IDs in advance; then measure **Precision@1**, **Recall@3** and **Mean Reciprocal Rank** for search. For chatbot responses, manually inspect whether claims are actually supported by a named retrieved source and whether changing rules are clearly qualified. Track cases where the right response is “not verifiable from the current corpus.”

For NLP processing, compare tokenization on at least five tricky strings, annotate stemming/lemmatization errors and report named-entity and sentence segmentation limitations. Generated metrics must be accompanied by manual interpretation.

## 6. Deliverables and next steps

| Stage | Deliverable | Status |
|---|---|---|
| A | Confirm institution, English, size and text types | **Defined; lecturer must approve genre mix** |
| B | 20 source-attributed UTF-8 corpus texts; metadata and validator | **Included** |
| C | Week 1 corpus and linguistic inspection | **Runnable notebook provided; run and interpret** |
| D | Week 2 tokenizer and sentence-segmentation experiments | **Runnable notebook provided; run and interpret** |
| E | Week 3 stemming, lemmatization and WordNet | **Runnable notebook provided; run and interpret** |
| F | Search engine and ranking evaluation | **Not yet implemented** |
| G | Autocomplete and grounded chatbot UI | **Not yet implemented** |
| H | Evaluation, screenshots, report and presentation | **Not yet implemented** |

## 7. Limitations and academic integrity

This corpus is an instructor-facing, educational derivative of university pages. It has only 20 short documents, so it cannot provide comprehensive coverage. Some source material is in Albanian and has been summarized in English, which limits direct quotation and exact-rule matching. Historical regulations are not assumed current. Sources may change after 8 November 2026; the project records retrieval context and must recheck them when deployed. The text type mix is proposed, not lecturer-approved. The notebooks are source code with exercises; **results are produced when the student executes them** and should not be represented as already measured.

