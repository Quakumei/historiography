#  Составление историографического обзора через машинное обучение

## Install dependencies

```bash
python -m venv .venv
.venv/bin/activate
pip install -r requirements.txt
```

## Building a dataset

To build dataset, run

```bash
python -m src.historiography.dataset.make_dataset
```

## Net Graph visualization

To build and open net graph visualization, run

```bash
python -m src.historiography.analysis.authors
```

## Dates extraction

To extract dates from dataset, run

```bash 
python -m src.historiography.analysis.dates
```

## LLM chatbot

To chat with data, refer to chat_with_historiography.ipynb