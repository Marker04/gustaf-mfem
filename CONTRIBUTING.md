# Contributing
gustaf welcomes and appreciates discussions, issues and pull requests!

## Quick start
Once the repo is forked, one possible starting point would be creating a new python environments, for example, using [conda](https://docs.conda.io/en/latest/miniconda.html) with `python=3.9`
```bash
conda create -n gustafenv python=3.9
git clone git@github.com:<path-to-your-fork>
cd gustaf
git checkout -b new-feature0
python3 setup.py develop
```

## Style / implementation preferences
gustaf implementations tries to follow [pep8](pep8.org)'s suggestion closely.
- use `if` and `raise` instead of `assert`
- no complex comphrehensions: preferably fits in a line, 2 lines max if it is totally necessary
- use first letter abbreviations in element loops:  `for kv in knot_vectors`
- use `i`, `j`, `k`, `l` for pure index: `for i, kv in enumerate(knot_vectors)`
- if a new feature would open doors to more related functionalities, consider a helper class
- try to avoid looping possibly giant entries  
Followings are covered by [auto formatting](https://github.com/tataratat/gustaf/blob/main/CONTRIBUTING.md#automatic-formatting--style-check):
- vertical alignment only with spaces with multiples of indent width (tip: adding trailing commas will vertilcally align/list all the entries in parenthesis/bracket/brace)
- put closing brackets on a separate line, dedented



### Automatic formatting / style check
gustaf uses combination of [yapf](https://github.com/google/yapf) and [autopep8](https://github.com/hhatto/autopep8) for automatic formatting. Then [flake8](https://github.com/pycqa/flake8) to double check everything.
```bash
cd <gustaf-root>
yapf -i -r gustaf examples tests 
autopep8 --select=W291,W292,W293,W504,E265,E501,E711,E722 -r -i --aggressive gustaf examples tests
flake8 gustaf examples tests
```

## Local docs build
To check if documentations look as intended, you can build it locally.
Remember, `spline` extentions will be empty if you don't have `splinepy` available.
```bash
pip install -r ./docs/requirements.txt
sphinx-apidoc -f -t docs/source/_templates -o docs/source gustaf
sphinx-build -b html docs/source docs/build
```
Now, you can check documentations by opening `docs/build/index.html` with a browser.


## Pull request suggessions
gustaf is a successor of gustav, which was an internal/experimental library.
Until all the functionalities are fully transferred, it may go through several dramatic changes.
Followings are gentle suggestions for PRs, so that the pre-alpha phase can end as soon as possible:
- small, separable features
- unit tests  
On the other hand, it is perfect time for suggestions / requests / feedbacks, so let us know!
