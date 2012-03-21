#!/usr/bin/env python

"""
Determines the concatenation order of JavaScript files by scanning JSLint
/*global ... */ declarations.
"""

import re
import sys

def slurp(filename):
    with open(filename) as f:
        return f.read()

DEPS_RE = re.compile(r'/\*global ([^*]+)\*/', re.M)

def js_dependencies(filename):
    """
    Finds a script's external JavaScript dependencies as declared in its
    /*global...*/ block.
    """
    match = DEPS_RE.search(slurp(filename))
    return match and [dep.strip().split(':')[0] for dep in match.group(1).split(',')]

def declaration_re(js_identifiers):
    """
    Constructs a regexp that matches top-level declarations of JavaScript
    identifiers.
    """
    return re.compile(r'^var [^;]%(names)s|^function %(names)s' %
                        {'names': r'\b(%s)\b' % '|'.join(js_identifiers)}, re.M)

def declaring_scripts(js_identifiers, filenames):
    """
    Finds the scripts that declare one or more of `js_identifiers'.
    """
    if not js_identifiers: return []
    decl_re = declaration_re(js_identifiers)
    decls = {}
    for f in filenames:
        matches = decl_re.findall(slurp(f))
        if matches: decls[f] = [m[1] for m in matches]
    return decls

def dependency_graph(filenames):
    """
    Returns a dependency graph, represented as a mapping of filenames to their
    list of dependency filenames.
    """
    graph = {}
    for f in filenames:
        others = filenames[:]
        others.remove(f)
        graph[f] = set(declaring_scripts(js_dependencies(f), others))
    return graph

def topological_ordering(graph):
    """
    Returns a topological ordering for nodes in `graph'.
    """
    # This algorithm mutates `graph', so make a copy
    graph = dict((n, deps.copy()) for (n, deps) in graph.items())

    order = []

    # Start with nodes that have no dependencies
    remaining = set(n for (n, deps) in graph.items() if not deps)

    # Remove edges from the graph as dependencies are resolved. If any edges
    # remain at the end of the process, at least one cycle exists.
    while remaining:
        n = remaining.pop()
        order.append(n)
        dependents = [m for (m, deps) in graph.items() if n in deps]
        for m in dependents:
            dependencies = graph[m]
            dependencies.remove(n)
            if not dependencies:
                remaining.add(m)

    # TODO: improve error reporting
    cycles = [n for (n, deps) in graph.items() if deps]
    if cycles:
        raise Exception('cycle(s) detected: %s' % cycles)

    return order

if __name__ == '__main__':
    print ' '.join(topological_ordering(dependency_graph(sys.argv[1:])))
