---
license: odc-by
task_categories:
- text-generation
language:
- en
pretty_name: OLMo 2 Mix (November 2024)
size_categories:
- 1B<n<10B

configs:
  - config_name: default
    data_files:
      - split: train
        path: data/**/*
    features:
    - name: bff_contained_ngram_count_before_dedupe
      dtype: int64
    - name: language_id_whole_page_fasttext
      dtype: string
    - name: metadata
      dtype: string
    - name: previous_word_count
      dtype: string
    - name: text
      dtype: string
    - name: url
      dtype: string
    - name: warcinfo
      dtype: string
    - name: fasttext_openhermes_reddit_eli5_vs_rw_v2_bigram_200k_train_prob
      dtype: string
    - name: id
      dtype: string
    - name: doc
      dtype: string
    - name: added
      dtype: string
    - name: created
      dtype: string
    - name: source
      dtype: string
    - name: attributes
      dtype: string
    - name: version
      dtype: string
  - config_name: algebraic-stack
    data_files:
      - split: train
        path: data/algebraic-stack/**/*
    features:
    - name: text
      dtype: string
    - name: added
      dtype: string
    - name: created
      dtype: string
    - name: attributes
      dtype: string
    - name: doc
      dtype: string
    - name: id
      dtype: string
    - name: metadata
      dtype: string
    - name: source
      dtype: string
    - name: version
      dtype: string
  - config_name: arxiv
    data_files:
      - split: train
        path: data/arxiv/**/*
    features:
    - name: text
      dtype: string
    - name: added
      dtype: string
    - name: created
      dtype: string
    - name: attributes
      dtype: string
    - name: doc
      dtype: string
    - name: id
      dtype: string
    - name: metadata
      dtype: string
    - name: source
      dtype: string
    - name: version
      dtype: string
  - config_name: dclm
    data_files:
      - split: train
        path: data/dclm/**/*
    features:
    - name: bff_contained_ngram_count_before_dedupe
      dtype: int64
    - name: language_id_whole_page_fasttext
      dtype: string
    - name: metadata
      dtype: string
    - name: previous_word_count
      dtype: string
    - name: text
      dtype: string
    - name: url
      dtype: string
    - name: warcinfo
      dtype: string
    - name: fasttext_openhermes_reddit_eli5_vs_rw_v2_bigram_200k_train_prob
      dtype: string
    - name: id
      dtype: string
    - name: doc
      dtype: string
    - name: added
      dtype: string
    - name: created
      dtype: string
    - name: source
      dtype: string
    - name: attributes
      dtype: string
    - name: version
      dtype: string
  - config_name: open-web-math
    data_files:
      - split: train
        path: data/open-web-math/**/*
    features:
    - name: text
      dtype: string
    - name: added
      dtype: string
    - name: created
      dtype: string
    - name: attributes
      dtype: string
    - name: doc
      dtype: string
    - name: id
      dtype: string
    - name: metadata
      dtype: string
    - name: source
      dtype: string
    - name: version
      dtype: string
  - config_name: pes2o
    data_files:
      - split: train
        path: data/pes2o/*
    features:
    - name: text
      dtype: string
    - name: added
      dtype: string
    - name: created
      dtype: string
    - name: attributes
      dtype: string
    - name: doc
      dtype: string
    - name: id
      dtype: string
    - name: metadata
      dtype: string
    - name: source
      dtype: string
    - name: version
      dtype: string
  - config_name: starcoder
    data_files:
      - split: train
        path: data/starcoder/**/*
    features:
    - name: text
      dtype: string
    - name: added
      dtype: string
    - name: created
      dtype: string
    - name: attributes
      dtype: string
    - name: doc
      dtype: string
    - name: id
      dtype: string
    - name: metadata
      dtype: string
    - name: source
      dtype: string
    - name: version
      dtype: string
  - config_name: wiki
    data_files:
      - split: train
        path: data/wiki/*
    features:
    - name: text
      dtype: string
    - name: added
      dtype: string
    - name: created
      dtype: string
    - name: attributes
      dtype: string
    - name: doc
      dtype: string
    - name: id
      dtype: string
    - name: metadata
      dtype: string
    - name: source
      dtype: string
    - name: version
      dtype: string
---

# OLMo 2 (November 2024) Pretraining set

Collection of data used to train OLMo-2-1124 models. The majority of this dataset comes from DCLM-Baseline with no additional filtering, but we provide the explicit breakdowns below.

| Name            | Tokens | Bytes (uncompressed) | Documents | License   |
|-----------------|--------|----------------------|-----------|-----------|
| DCLM-Baseline   | 3.70T  | 21.3TB               | 2.95B     | CC-BY-4.0 |
| Arxiv           | 20.8B  | 77.2GB               | 3.95M     | ODC-BY    |
| pes2o           | 58.6B  | 412GB                | 38M       | ODC-BY    |
| starcoder       | 83.0B  | 458GB                | 78.7M     | ODC-BY    |
| Algebraic-stack | 11.8B  | 44.0GB               | 2.83M     | ODC-BY    |
| OpenWebMath     | 12.2B  | 47.23GB              | 2.89M     | ODC-BY    |
| Wiki            | 3.66B  | 18.1GB               | 6.17M     | ODC-BY    |
| Total           | 3.90T  | 22.4TB               | 3.08B     | ODC-BY    |




Please refer to the OLMo2 Tech Report for further details. 

## Licensing Information

This **collection** is released under the **Open Data Commons Attribution License (ODC-By) v1.0** [license](https://opendatacommons.org/licenses/by/1-0/). The use of this dataset is also subject to [CommonCrawl's Terms of Use](https://commoncrawl.org/terms-of-use).

## Citation
A technical manuscript is forthcoming!
