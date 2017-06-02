# Copyright (c) 2015-2017 Antonino Ingargiola
# License: MIT
"""
nbrun - Run an Jupyter/IPython notebook, optionally passing arguments.

USAGE
-----

Copy this file in the folder containing the master notebook used to
execute the other notebooks. Then use `run_notebook()` to execute
notebooks.
"""

import time
from pathlib import Path
from IPython.display import display, FileLink
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter

__version__ = '0.2'


def dict_to_code(mapping):
    """Convert input dict `mapping` to a string containing python code.

    Each key is the name of a variable and each value is
    the variable content. Each variable assignment is separated by
    a newline.

    Keys must be strings, and cannot start with a number (i.e. must be
    valid python identifiers). Values must be objects with a string
    representation (the result of repr(obj)) which is valid python code for
    re-creating the object.
    For examples, numbers, strings or list/tuple/dict
    of numbers and strings are allowed.

    Returns:
        A string containing the python code.
    """
    lines = ("{} = {}".format(key, repr(value))
             for key, value in mapping.items())
    return '\n'.join(lines)


def run_notebook(notebook_path, nb_kwargs=None, suffix='-out',
                 out_path_ipynb=None, out_path_html=None,
                 kernel_name=None, working_dir='./',
                 timeout=3600, execute_kwargs=None,
                 save_ipynb=True, save_html=False,
                 insert_pos=1, hide_input=False, display_links=True,
                 return_nb=False):
    """Runs a notebook and saves the output in a new notebook.

    Executes a notebook, optionally passing "arguments"
    similarly to passing arguments to a function.
    Notebook arguments are passed in a dictionary (`nb_kwargs`) which is
    converted into a string containing python assignments. This string is
    inserted in the template notebook as a code cell. The code assigns
    variables which can be used to control the execution. When "calling"
    a notebook, you need to know which arguments (variables) to pass.
    Unlike normal python functions, no check is performed on the input
    arguments. For sanity, we recommended describing the variables that
    can be assigned using a markdown cell at the beginning of the template
    notebook.

    Arguments:
        notebook_path (pathlib.Path or string): input notebook filename.
            This is the notebook to be executed (i.e. template notebook).
        nb_kwargs (dict or None): If not None, this dict is converted to a
            string of python assignments using the dict keys as variables
            names and the dict values as variables content. This string is
            inserted as code-cell in the notebook to be executed.
        suffix (string): suffix to append to the file name of the executed
            notebook. Argument ignored if `out_notebook_path` is not None.
        out_path_ipynb (pathlib.Path, string or None): file name for the
            output ipynb notebook. If None, the ouput ipynb notebook has
            the same name as the input notebook plus a suffix, specified
            by the `suffix` argument. If not None, `suffix` is ignored.
            If argument `save_ipynb` is False this argument is ignored.
        out_path_html (pathlib.Path, string or None): file name for the
            output HTML notebook. If None, the ouput HTML notebook has
            the same name as the input notebook plus a suffix, specified
            by the `suffix` argument. If not None, `suffix` is ignored.
            If argument `save_html` is False this argument is ignored.
        kernel_name (string or None): name of the kernel used to execute the
            notebook. Use the default kernel if None.
        working_dir (string or Path): the folder the kernel is started into.
        timeout (int): max execution time (seconds) for each cell before the
            execution is aborted.
        execute_kwargs (dict): additional arguments passed to
            `ExecutePreprocessor`.
        save_ipynb (bool): if True, save the output notebook in ipynb format.
            Default True.
        save_html (bool): if True, save the output notebook in HTML format.
            Default False.
        insert_pos (int): position of insertion of the code-cell containing
            the input arguments. Default is 1 (i.e. second cell). With this
            default, the input notebook can define, in the first cell, default
            values of input arguments (used when the notebook is executed
            with no arguments or through the Notebook GUI).
        hide_input (bool): whether to create a notebook with input cells
            hidden (useful to remind user that the auto-generated output
            is not meant to have the code edited.
        display_links (bool): if True, display/print "link" of template and
            output notebooks. Links are only rendered in a notebook.
            In a text terminal, links are displayed as full file names.
        return_nb (bool): if True, returns the notebook object. If False
            returns None. Default False.
    """
    timestamp_cell = ("**Executed:** %s\n\n**Duration:** %d seconds.\n\n"
                      "**Autogenerated from:** [%s](%s)")
    if nb_kwargs is None:
        nb_kwargs = {}
    else:
        header = '# Cell inserted during automated execution.'
        code = dict_to_code(nb_kwargs)
        code_cell = '\n'.join((header, code))

    notebook_path = Path(notebook_path)
    if not notebook_path.is_file():
        raise FileNotFoundError("Path '%s' not found." % notebook_path)

    def check_out_path(notebook_path, out_path, ext, save):
        if out_path is None:
            out_path = Path(notebook_path.parent,
                            notebook_path.stem + suffix + ext)
        out_path = Path(out_path)
        if save and not out_path.parent.exists():
            msg = "Folder of the output %s file was not found:\n - %s\n."
            raise FileNotFoundError(msg % (ext, out_path_ipynb.parent))
        return out_path

    out_path_ipynb = check_out_path(notebook_path, out_path_ipynb,
                                    ext='.ipynb', save=save_ipynb)
    out_path_html = check_out_path(notebook_path, out_path_html,
                                   ext='.html', save=save_html)
    if display_links:
        display(FileLink(str(notebook_path)))

    if execute_kwargs is None:
        execute_kwargs = {}
    execute_kwargs.update(timeout=timeout)
    if kernel_name is not None:
        execute_kwargs.update(kernel_name=kernel_name)
    ep = ExecutePreprocessor(**execute_kwargs)
    nb = nbformat.read(str(notebook_path), as_version=4)

    if hide_input:
        nb["metadata"].update({"hide_input": True})

    if len(nb_kwargs) > 0:
        nb['cells'].insert(insert_pos, nbformat.v4.new_code_cell(code_cell))

    start_time = time.time()
    try:
        # Execute the notebook
        ep.preprocess(nb, {'metadata': {'path': working_dir}})
    except:
        # Execution failed, print a message then raise.
        msg = ('Error executing the notebook "%s".\n'
               'Notebook arguments: %s\n\n'
               'See notebook "%s" for the traceback.' %
               (notebook_path, str(nb_kwargs), out_path_ipynb))
        print(msg)
        timestamp_cell += '\n\nError occurred during execution. See below.'
        raise
    finally:
        # Add timestamping cell
        duration = time.time() - start_time
        timestamp_cell = timestamp_cell % (time.ctime(start_time), duration,
                                           notebook_path, out_path_ipynb)
        nb['cells'].insert(0, nbformat.v4.new_markdown_cell(timestamp_cell))
        # Save the executed notebook to disk
        if save_ipynb:
            nbformat.write(nb, str(out_path_ipynb))
            if display_links:
                display(FileLink(str(out_path_ipynb)))
        if save_html:
            html_exporter = HTMLExporter()
            body, resources = html_exporter.from_notebook_node(nb)
            with open(str(out_path_html), 'w') as f:
                f.write(body)
        if return_nb:
            return nb
