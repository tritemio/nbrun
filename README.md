# nbrun

Nbrun automates the execution of Jupyter Notebooks,
passing arguments for parametrization. 
Nbrun offers a simple yet effective way to remove code duplication 
and manual steps, allowing to build automated and self-documented 
analysis pipelines. 

Nbrun contains a single function (`run_notebook()`) which allows to call/execute
notebooks, optionally passing arguments. With nbrun, you can call a notebook
with arguments, similarly to calling a function with arguments.
When called from a notebook, `run_notebook()` shows links to the template and executed
notebooks.

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

# Implementation

The mechanism is "low-tech", yet effective. The input arguments are contained in a
dictionary. The function `run_notebook` inserts a code cell after the first cell
of the template notebook with a series of variable assignments which correspond
to the arguments in the dictionary. For example, if we pass `{'data_id': 1}`, the
following code cell will be inserted:

```
data_id = 1
```

Why after the first cell? Conventionally, the template notebook contains
assignment to variables used as "input arguments" in the first cell. These are
the default values and allow the template notebook to be executed independently.
When we pass an argument, it will be inserted in the second cell, overriding
the default arguments.

# Limitations

The dict containing input arguments is converted to a string containing
python-code which assigns a variable for each argument. For this reason, you
cannot pass arbitrary objects, but only objects with a complete
"literal representation" (i.e. using `repr()`).
Arguments can be strings, numbers and tuple/list/dict of strings
and numbers, but cannot be a function, for example. Given the typical use-case,
this limitation is not very critical.

Also, differently from calling a real python function, no check is performed 
on the input arguments. There is not formal "notebook signature", analogous 
of the function signature. The user needs to make sure she/he is passing the 
right arguments when calling/executing a notebook. As a future idea, a "signature"
can be embedded in the template notebook metadata, and checked by
`run_notebook()` before executing the notebook.

# Development
*nbrun* contains only a single function ``run_notebook`` to run notebooks.
There is also a small helper function used internally to convert a dict
of arguments to python assignments.

At the moment you have to copy the file ``nbrun.py`` into you project folder.
Maybe I'll turn it into a python package one day (PR welcome!).

Some users asked about future development. I don't think there is much functionality 
left to be added. So, I don't forsee big changes in the future except for compatibility 
fixes and small API tweaks.

# Alternatives

- [runipy](https://github.com/paulgb/runipy)
- [nbparameterise](https://github.com/takluyver/nbparameterise)

**Runipy** was the first tool to provide batch execution of notebooks, even before Jupyter
was born from IPython. Nowadays most of the funtionality is included in nbconvert.
With runipy you can pass arguments to notebooks only thorugh environment variables.

**nbparameterise** uses AST instead of eval to pass arguments (which is a safer and more robust choice).
However the code is much more complex and, last time I checked, it didn't support passing list or dict
as arguments.
I thought about improving nbparameterise but at the end I didn't find the time 
since nbrun was already working for my use case.

