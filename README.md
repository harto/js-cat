This script determines one (of potentially many) concatenation orderings for a
set of JavaScript files. It relies on dependencies to be declared in a JSLint
`/*global ... */` declaration.

Example usage:

    $ python dependency-order.py /my/project/*.js
