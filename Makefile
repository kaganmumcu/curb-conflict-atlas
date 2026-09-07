.PHONY: setup data analysis notebook test all

setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

data:
	.venv/bin/python -m src.pipeline --refresh

analysis:
	.venv/bin/python -m src.pipeline

notebook:
	.venv/bin/python scripts/build_notebook.py
	JUPYTER_PATH=.venv/share/jupyter MPLCONFIGDIR=.mplconfig IPYTHONDIR=.ipython .venv/bin/python -m jupyter nbconvert --execute --to notebook --inplace notebooks/curb_conflict_atlas.ipynb

test:
	.venv/bin/python -m unittest discover -s tests -v

all: analysis notebook test
