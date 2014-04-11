=======
pdfdiff
=======
pdfdiff is a tool that allows you to compare 2 PDF files and see differences
marked with red


.. contents::

Install
=======

    ::

        $: pip install pdfdiff

        or

        $: python setup.py install


How it works?
=============

    $: pdfdiff -i testing.pdf -o expected.pdf -d /tmp/output/directory


See more options::

    usage: pdfdiff.py.bak [-h] [-i INPUT] [-o OUTPUT] [-d DIRECTORY]

    optional arguments:
      -h, --help            show this help message and exit
      -i INPUT, --input INPUT
                            PDF file path or URL to compare
      -o OUTPUT, --output OUTPUT
                            PDF file path or URL to compare with
      -d DIRECTORY, --directory DIRECTORY
                            Output directory
