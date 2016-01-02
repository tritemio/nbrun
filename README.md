# nbrun

Batch-run Jupyter IPython notebooks (optionally) passing arguments. Nbrun
contains a single function (`run_notebook`) which allows to call/execute a
notebook, optionally passing arguments, roughly similar to passing arguments
to a function.

Nbrun is a small wapper function around [nbconvert](https://github.com/jupyter/nbconvert).

# Usage

Clone the repo and execute the master notebook. To use in a new project,
copy the file `nbrun.py` in your project's notebook folder.

# Rationale

Oftentimes we write notebooks to analyze a dataset, then we want to use the same
notebook for a different dataset. For reproducibility and for quickly finding
results later on, it is good practice to save a fully executed notebook for each
data file. So, naturally, we start making copies of the original notebook to
process each additional data file. But every time we improve or fix the notebook
we need to replicate the changes in all the other similar notebooks.

Enters nbrun. With nbrun we can keep a single "template" notebook which performs
the analysis. The template notebook takes one (or more) arguments as input (e.g.
the dataset file name or an ID). A second "master" notebook is used to execute
the template notebook in batch, once for each input argument. Each time the
template is executed with a particular set of arguments, it is saved to disk. At
the end we obtain a fully executed notebook for each dataset/arguments, and a
single template notebook to modify when we fix/improve the analysis.

# How

The mechanism is rudimentary. The input arguments are contained in a
dictionary. The function `run_notebook` inserts a code cell after the first cell
of the template notebook with a series of variable assignments which correspond
to the arguments dictionary. For example, if we pass `{'data_id': 1}`, the
following code cell will be inserted:

```
data_id = 1
```

Why after the first cell? Conventionally, the template notebook contains
assignment to variables used as "input arguments" in the first cell. This are
the default values and allow the template notebook to be executed independently.
When we pass an argument this will be inserted in the second cell, overriding
the default arguments.

# Limitations

The input arguments are transformed in a series of assignments, which needs to
be some valid python code. For this reason, you can not pass arbitrary objects
but only objects whose representation (`repr`) is a "literal representation".
For example, arguments can be strings, numbers and tuple/list/dict of strings
and numbers. This is more than enough to cover the use-case.

Also, differently from calling a real function, no check is performed on the
input arguments. There is not formal "notebook signature" (like function
signature). The user needs to make sure she/he is passing the right arguments
when calling/executing a notebook.
