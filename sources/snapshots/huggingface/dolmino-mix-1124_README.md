---
license: odc-by
task_categories:
- text-generation
pretty_name: DOLMino Mix (November 2024)
size_categories:
- 100M<n<1B
language:
- en
configs:
  - config_name: default
    data_files:
      - split: train
        path: data/**/*
  - config_name: dclm
    data_files:
      - split: train
        path: data/dclm/**/*        
  - config_name: flan
    data_files:
      - split: train
        path: data/flan/*  
  - config_name: pes2o
    data_files:
      - split: train
        path: data/pes2o/*  
  - config_name: stackexchange
    data_files:
      - split: train
        path: data/stackexchange/*  
  - config_name: wiki
    data_files:
      - split: train
        path: data/wiki/*  
  - config_name: stackexchange
    data_files:
      - split: train
        path: data/stackexchange/*
        
  - config_name: math
    data_files:
      - split: train
        path: data/math/**/*
    features:
      - name: id
        dtype: string
      - name: text
        dtype: string
      - name: source
        dtype: string
      - name: added
        dtype: string
      - name: created
        dtype: string
      - name: version
        dtype: string
      - name: attributes
        dtype: string
      - name: instruction
        dtype: string
      - name: prompt
        dtype: string
      - name: text_token_length
        dtype: int64
      - name: text_length
        dtype: int64
      - name: len
        dtype: int64
      - name: url
        dtype: string
      - name: __index_level_0__
        dtype: int64
      - name: openai_response
        dtype:
          struct:
            - name: is_math
              dtype: bool
      - name: question
        dtype: string
      - name: answer
        dtype: string
      - name: original_gsm_id
        dtype: string
      - name: metadata
        dtype: string
      - name: meta
        dtype:
          struct:
            - name: type
              dtype: string
            - name: query
              dtype: string
            - name: original_question
              dtype: string
            - name: response
              dtype: string
      - name: repository_name
        dtype: string
      - name: func_path_in_repository
        dtype: string
      - name: func_name
        dtype: string
      - name: language
        dtype: string
      - name: func_code_string
        dtype: string
      - name: func_code_tokens
        dtype:
          sequence: string
      - name: func_documentation_string
        dtype: string
      - name: func_documentation_tokens
        dtype:
          sequence: string
      - name: split_name
        dtype: string
      - name: func_code_url
        dtype: string
      - name: Language=
        dtype: string
      - name: License=
        dtype: string
      - name: Meta_Link=
        dtype: string
      - name: audience
        dtype: string
      - name: format
        dtype: string
      - name: seed_data
        dtype: string
---

<img alt="Dolmino Logo." src="dolmino.png" width="400px">

# DOLMino dataset mix for OLMo2 stage 2 annealing training. 

Mixture of high-quality data used for the second stage of OLMo2 training. 

## Source Sizes

| Name                    | Category     | Tokens | Bytes (uncompressed) | Documents | License                  |
|-------------------------|--------------|--------|----------------------|-----------|--------------------------|
| DCLM                    | HQ Web Pages | 752B   | 4.56TB               | 606M      | CC-BY-4.0                |
| Flan                    | HQ Web Pages | 17.0B  | 98.2GB               | 57.3M     | ODC-BY                   |
| Pes2o                   | STEM Papers  | 58.6B  | 413GB                | 38.8M     | ODC-BY                   |
| Wiki                    | Encyclopedic | 3.7B   | 16.2GB               | 6.17M     | ODC-BY                   |
| StackExchange           | CodeText     | 1.26B  | 7.72GB               | 2.48M     | CC-BY-SA-{2.5, 3.0, 4.0} |
| TuluMath                | Synth Math   | 230M   | 1.03GB               | 220K      | ODC-BY                   |
| DolminoSynthMath        | Synth Math   | 28.7M  | 163MB                | 725K      | ODC-BY                   |
| TinyGSM-MIND            | Synth Math   | 6.48B  | 25.52GB              | 17M       | ODC-BY                   |
| MathCoder2              | Synth Math   | 3.87B  | 18.48GB              | 2.83M     | Apache 2.0               |
| Metamath-owmfilter      | Math         | 84.2M  | 741MB                | 383K      | CC-BY-SA-4.0             |
| CodeSearchNet-owmfilter | Math         | 1.78M  | 29.8MB               | 7.27K     | ODC-BY                   |
| GSM8K                   | Math         | 2.74M  | 25.3MB               | 17.6K     | MIT                      |
| Total                   |              | 843B   | 5.14TB               | 732M      | ODC-BY                   |



Where the breakdowns of each of TuluMath and DolminoSythMath are as follows:
| Name                   | Category         | Tokens | Bytes (uncompressed) | Documents | License |
|------------------------|------------------|--------|----------------------|-----------|---------|
| Personahub_math_v5     | TuluMath         | 191M   | 825MB                | 150K      | ODC-BY  |
| Personahub_math_interm | TuluMath         | 19.7M  | 82.9MB               | 20k       | ODC-BY  |
| Personahub_math_grade  | TuluMath         | 21.8M  | 119.7MB              | 50K       | ODC-BY  |
| BasicMathMJ            | DolminoSynthMath | 11.1M  | 84.7MB               | 664K      | ODC-BY  |
| GSM8K-synth            | DolminoSynthMath | 539K   | 8.19MB               | 7924      | ODC-BY  |
| GSM_MIND               | DolminoSynthMath | 17.1M  | 70.8MB               | 52K       | ODC-BY  |

Please refer to the OLMo2 Tech Report for further details. 

## Mix Compositions
The above tables simply refer to the total size and token counts of each of the individual sources. In practice we perform stage 2 training with either a 50B, 100B, or 300B token mixture taken from the above sources. In general, this is composed of roughly a 50% token yield from DCLM, and 50% token yield from the remaining sources. The table below summarizes this mixture:

| Source | 50B | | 100B | | 300B | |
|--------|-----|-----|------|-----|------|-----|
| | Source % | Mix % | Source % | Mix % | Source % | Mix % |
| DCLM Baseline | 3.23 | 47.2 | 6.85 | 50.2 | 20.78 | 51.9 |
| FLAN | 50.0 | 16.6 | 100 | 16.7 | 200 | 11.3 |
| pes2o | 5.15 | 5.85 | 16.7 | 9.52 | 100 | 19.4 |
| Wiki | 100 | 7.11 | 100 | 3.57 | 400 | 4.86 |
| StackExchange | 100 | 2.45 | 200 | 2.47 | 400 | 1.68 |
| Stage 2 Math | 100 | 20.8 | 200 | 17.5 | 400 | 10.8

Where "Stage 2 Math" above refers to all sources with category "Math" or "Synth Math" 


## Licensing Information

This **collection** is released under the **Open Data Commons Attribution License (ODC-By) v1.0** [license](https://opendatacommons.org/licenses/by/1-0/). The use of this dataset is also subject to [CommonCrawl's Terms of Use](https://commoncrawl.org/terms-of-use).

## Citation
A technical manuscript is forthcoming! 
