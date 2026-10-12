# Literature Review: Formal Language Models for Resume Screening

ResumeLens uses classical formal-language models to decide whether the qualifications **explicitly written** in a résumé satisfy a professional-profile pattern. This review situates that choice against automated résumé parsing, skill extraction, and finite-state methods in NLP, and records the design implications for the four pipeline stages.

## 1. The résumé-screening problem

Recruiters often spend less than a minute on a résumé and rely on keywords, which makes consistent, explainable screening difficult (Maheshwari et al., 2016). Automated systems typically (i) extract entities (name, contact, education, skills), (ii) normalize spelling and synonyms, and (iii) match the result against a job or profile. Yu et al. (2005) already framed résumé analysis as a two-pass information-extraction task: segment the document, then label fields. Later surveys of NLP for HR describe skill extraction as the core of algorithmic hiring, with methods ranging from taxonomies and rules to embeddings and large language models (Khaouja et al., 2021; Qin et al., 2024).

Two properties of the problem matter for ResumeLens:

- The **same qualification** appears under many surface forms (`JS` / `Javascript` / `JavaScript`; `sklearn` / `scikit-learn`).
- A **profile** is a combination of qualifications with optionality (e.g. REST APIs optional for Full Stack, Git optional for Data Analyst), not a ranked similarity score.

The assignment explicitly forbids ranking or hiring decisions. That rules out the dominant industrial pattern—cosine similarity or a learned ranker between résumé and job description (Gugnani & Misra, 2020; Murthy et al., 2023)—and favours an **acceptor**: a string is in the language of the profile or it is not.

## 2. Extraction: regular expressions vs. statistical NLP

Production résumé parsers mix regular expressions (contact details, dates, years of experience) with named-entity recognition for names, organisations and free-text skills (Sougandh et al., 2023; Murthy et al., 2023). Maheshwari et al. (2016) note that even in an ML pipeline, dates and similar fields still need a regex normalisation pass because of spelling variation.

Regex is the right tool when the **language of the field is regular**: emails, URLs, phone numbers, and a closed lexicon of technology names. It is the wrong tool for paraphrase (`experience building predictive models` vs. `machine-learning model development`) and for layout-heavy PDFs. ResumeLens therefore:

- uses `re` only on **plain text** and a **finite catalogue** of skills (`contracts.CANONICAL`);
- does not attempt semantic inference of qualifications that are not written.

This is a deliberate trade-off: high transparency and a precise formal model, at the cost of recall on unseen synonyms. Transformer-based extractors (BERT-family job/résumé matchers) outperform keyword systems on F1 (see the comparative review of NLP in recruitment systems, 2025) but do not yield a 5-tuple or a grammar the course can mark.

## 3. Normalisation: finite-state transducers

Finite-state transducers (FSTs) are the standard formalisation of lexicon mapping in computational morphology and NLP (Roche & Schabes, 1997; Beesley & Karttunen, 2003). An FST is a 7-tuple \(M = (Q, \Sigma, \Gamma, \delta, \omega, q_0, F)\): it reads a surface string over \(\Sigma\) and writes a canonical string over \(\Gamma\).

In résumé data the same idea appears informally as synonym lists and lower-casing. Modelling it as an FST makes the mapping **checkable** (each variant is a path) and **composable** with the later DFA, whose alphabet \(\Sigma\) is exactly \(\Gamma\) of the transducer. Character-level tries (one transducer per category, plus a global union) keep \(|Q|\) linear in the total length of variants and emit the canonical token once, even when one variant is a prefix of another (`react` / `reactjs`).

Statistical spell-correction or embeddings could merge more variants, but they would blur the contract between Stage 2 and Stage 3: the DFA must see a **finite, named** alphabet.

## 4. Profile recognition: finite automata

A professional profile in ResumeLens is a regular language over canonical tokens: a concatenation of slots, each a non-empty (or optional) choice among symbols, with a fixed order. Regular languages are exactly those recognised by deterministic finite automata (Hopcroft, Motwani & Ullman, 2006; Sipser, 2012). A DFA \(M = (Q, \Sigma, \delta, q_0, F)\) is enough because:

- Stage 2 already sorts tokens into canonical order, so the automaton does not need to accept permutations;
- optionality is a skip over an optional slot, not \(\varepsilon\)-nondeterminism that would require an \(\varepsilon\)-NFA;
- each state encodes “last token consumed”, so \(|Q| = |\Sigma| + 1\).

Nondeterminism would only duplicate the same paths. Using a DFA also matches the course requirement to **name the automaton type from the 5-tuple**: unique \(\delta(q,a)\), no \(\lambda\)-transitions, finite \(\Sigma\).

This is the opposite of latent matching (CareerBERT, ESCO embeddings, LLM skill phrases), which cannot answer “which slot failed?” A rejecting DFA state corresponds to a missing required slot or an out-of-order/foreign token—useful both as a formal object and as an explanation in the DSL report.

## 5. Structured output: context-free grammars and textX

After classification, the candidate record is no longer a regular string: it has nested, repeated fields (contact entries, qualification groups, one verdict per profile). That is the classic jump from regular to **context-free** languages (Aho, Sethi & Ullman; the Chomsky hierarchy). Domain-specific languages implemented with **textX** (Dejanović et al., 2017) compile an EBNF-like grammar into a meta-model, so invalid profiles are rejected lexically or syntactically, and a validator can enforce semantic rules (unknown tokens, wrong group, verdict inconsistent with the automata).

HTML/Markdown generation from the validated model is a straightforward unparsing step; the grammar, not the template, is the specification of “what a candidate profile is”.

## 6. Positioning and limits

| Approach | Typical use | Fit for this project |
|---|---|---|
| Regex + gazetteer | Contact, closed skill lists | Stage 1 |
| FST / morphological lexicon | Surface → lemma | Stage 2 |
| DFA / regular expression of skills | Boolean profile patterns | Stage 3 |
| CFG / textX DSL | Structured, nested records | Stage 4 |
| NER + embeddings / LLMs | Open skill extraction, ranking | Out of scope (not explainable as 5/7-tuples; ranks candidates) |

ResumeLens is therefore **not** a hiring recommender. It is an executable formal specification of four profile languages, aligned with the literature on résumé IE where the pipeline is extract → normalise → match, but with each stage identified with a model from formal language theory.

Remaining gaps acknowledged by the same literature: PDF layout (Yu et al., 2005; Yao et al., 2023), long-tail skills not in the gazetteer, and fairness/bias when ML rankers are used (Qin et al., 2024). None of those are required to recognise an explicit, canonical qualification pattern.

## References

Beesley, K. R., & Karttunen, L. (2003). *Finite State Morphology*. CSLI.

Dejanović, I., Vaderna, R., Milosavljević, G., & Vuković, Ž. (2017). TextX: A Python tool for Domain-Specific Languages implementation. *Knowledge-Based Systems*, 115, 1–4.

Gugnani, A., & Misra, H. (2020). Implicit skills extraction using document embedding and its use in job recommendation. *AAAI*.

Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2006). *Introduction to Automata Theory, Languages, and Computation* (3rd ed.). Pearson.

Khaouja, I., Kassou, I., & Ghogho, M. (2021). A survey on skill identification from online job ads. *IEEE Access*.

Maheshwari, S., Sainani, A., & Reddy, P. K. (2016). Data-driven HR résumé analysis based on natural language processing and machine learning (arXiv:1606.05611).

Murthy, et al. (2023). Hybrid resume parsing and matching using RegEx and NER. Cited in IJIRT review on AI resume parsers.

Qin, C., et al. (2024). Natural language processing for human resources: A survey (arXiv:2410.16498).

Roche, E., & Schabes, Y. (Eds.). (1997). *Finite-State Language Processing*. MIT Press.

Sipser, M. (2012). *Introduction to the Theory of Computation* (3rd ed.). Cengage.

Sougandh, et al. (2023). Automated resume parsing with NER and regex. In reviews of AI resume parsers (IJIRT 171690).

Yu, K., Guan, G., & Zhou, M. (2005). Resume information extraction with cascaded hybrid model. *ACL*.
