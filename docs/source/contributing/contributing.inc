:orphan:

.. _contributing_howto:

Github workflow for your contribution
*************************************
The workflow GAMA maintains is described in more detail in this
`great blog post <https://blog.scottlowe.org/2015/01/27/using-fork-branch-git-workflow/>`_
by `@scott_lowe <https://twitter.com/scott_lowe>`_.
Here follows a short version with little explanation, just some commands.

First fork the GAMA Github repository:

    - visit `GAMA's Github page <https://github.com/PGijsbers/gama>`_
    - click the 'fork' button in the top-right corner.

Clone *your fork* to your local machine.
Find the URL behind the green button 'clone or download', it should look like this::

    git clone https://github.com/GITHUB_USER_NAME/gama.git

Add the original GAMA repository as an additional remote::

    git remote add upstream https://github.com/PGijsbers/gama.git

Create a branch to work on your contribution (from the directory that has your cloned repository)::

    git checkout -b <your_branch_name>

Now you can start working on your contribution!
Push your changes back to your ``origin`` remote (the name of the automatically added remote)::

    git push origin <your_branch_name>

If you are ready to have your changes added to the GAMA repository, open a pull request.
This can be done using the Github website, where a button should pop up on your fork's repository.

When opening a pull request, make sure you have:

    - updated the documentation
    - added tests where reasonable
    - refer to the issue and mention any additional information that might make reviewing the PR easier.

Running unit tests
******************
To run the unit tests, make sure optional dependencies for developers are installed.
From GAMA directory run::

    pip install -e .[test]

This installs test dependencies such as ``pytest`` and plugins.

The unit tests are separated into two suites: unit and system tests.
Unit tests are designed to test isolated functions quickly.
Due to the big configuration space and random nature of search,
it is impossible to test all scenarios thoroughly in unit tests.
System tests perform full AutoML runs (on tiny datasets) and are meant to pick up on things missed by unit tests.
To run a test suite run::

    pytest -sv -n 4 tests/SUITE

where ``SUITE`` is either ``unit`` or ``system``.
The ``-sv -n 4`` flags are optional, but give succinct feedback on what is being run (``-sv``) and run tests in parallel (``-n 4``).
For more information, run ``pytest -h``.

Generating Documentation
************************
The documentation is generated with `Sphinx <https://www.sphinx-doc.org/en/master/>`_.
Run::

    sphinx-build -b html docs\source docs\build

The html pages are now in the ``gama\docs\build`` directory.