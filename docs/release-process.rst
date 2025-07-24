.. _process:

Release process
---------------

.. note::
    The changelog is based on `Keep a Changelog <https://keepachangelog.com/en/1.1.0/>`_
    and it also uses the `towncrier.toml <https://towncrier.readthedocs.io/en/stable/markdown.html>`_

1. Generate build as CHANGELOG.md with towncrier

.. code-block:: console

    $ towncrier build --version <version-number> # e.g.: towncrier build --version 0.1.2

2. Go to Github Release UI.
3. Choose a tag and select 'create new tag and publish'.
4. Set title <name> <tag version> *e.g.: Agie 0.1.2*
5. Set the content based on CHANGELOG.md (copy and paste from it)
6. For the rst file, execute (needs pandoc installed on system):

.. code-block:: console

   $ pandoc --from=markdown --to=rst --output=NEWS.rst CHANGELOG.md

7. Update the documentation to use 'NEWS.rst' if isnt set yet, and run:

.. code-block:: console

    $ make clean # its important to execute this before
    $ make html

8. Now push these new file changes and submit the release.