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