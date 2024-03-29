"""A module to change reload() so that it acts recursively.
To enable it type:
    >>> import __builtin__, deep_reload
    >>> __builtin__.reload = deep_reload.reload
You can then disable it with:
    >>> __builtin__.reload = deep_reload.original_reload
    
Alternatively, you can add a dreload builtin alongside normal reload with:
    >>> __builtin__.dreload = deep_reload.reload
    
This code is almost entirely based on knee.py from the standard library.
"""

__author__ = "Nathaniel Gray <n8gray@caltech.edu>"
__version__ = 0.5
__date__ = "21 August 2001"

import sys, imp, builtins

# Replacement for __import__()
def deep_import_hook(name, globals=None, locals=None, fromlist=None):
#    if fromlist:
#        print 'Importing', fromlist, 'from module', name
#    else:
#        print 'Importing module', name
    parent = determine_parent(globals)
    q, tail = find_head_package(parent, name)
    m = load_tail(q, tail)
    if not fromlist:
        return q
    if hasattr(m, "__path__"):
        ensure_fromlist(m, fromlist)
    return m

def determine_parent(globals):
    if not globals or  "__name__" not in globals:
        return None
    pname = globals['__name__']
    if "__path__" in globals:
        parent = sys.modules[pname]
        assert globals is parent.__dict__
        return parent
    if '.' in pname:
        i = pname.rfind('.')
        pname = pname[:i]
        parent = sys.modules[pname]
        assert parent.__name__ == pname
        return parent
    return None

def find_head_package(parent, name):
    # Import the first 
    if '.' in name:
        # 'some.nested.package' -> head = 'some', tail = 'nested.package'
        i = name.find('.')
        head = name[:i]
        tail = name[i+1:]
    else:
        # 'packagename' -> head = 'packagename', tail = ''
        head = name
        tail = ""
    if parent:
        # If this is a subpackage then qname = parent's name + head
        qname = "%s.%s" % (parent.__name__, head)
    else:
        qname = head
    q = import_module(head, qname, parent)
    if q: return q, tail
    if parent:
        qname = head
        parent = None
        q = import_module(head, qname, parent)
        if q: return q, tail
    raise ImportError("No module named " + qname)

def load_tail(q, tail):
    m = q
    while tail:
        i = tail.find('.')
        if i < 0: i = len(tail)
        head, tail = tail[:i], tail[i+1:]
        mname = "%s.%s" % (m.__name__, head)
        m = import_module(head, mname, m)
        if not m:
            raise ImportError("No module named " + mname)
    return m

def ensure_fromlist(m, fromlist, recursive=0):
    for sub in fromlist:
        if sub == "*":
            if not recursive:
                try:
                    all = m.__all__
                except AttributeError:
                    pass
                else:
                    ensure_fromlist(m, all, 1)
            continue
        if sub != "*" and not hasattr(m, sub):
            subname = "%s.%s" % (m.__name__, sub)
            submod = import_module(sub, subname, m)
            if not submod:
                raise ImportError("No module named " + subname)

# Need to keep track of what we've already reloaded to prevent cyclic evil
found_now = {}

def import_module(partname, fqname, parent):
    global found_now
    if fqname in found_now:
        try:
            return sys.modules[fqname]    
        except KeyError:
            pass
    
    print('Reloading', fqname) #, sys.excepthook is sys.__excepthook__, \
            #sys.displayhook is sys.__displayhook__
    
    found_now[fqname] = 1
    try:
        fp, pathname, stuff = imp.find_module(partname,
                                              parent and parent.__path__)
    except ImportError:
        return None
        
    try:
        m = imp.load_module(fqname, fp, pathname, stuff)
    finally:
        if fp: fp.close()
        
    if parent:
        setattr(parent, partname, m)
        
    return m

def deep_reload_hook(module):
    name = module.__name__
    if '.' not in name:
        return import_module(name, name, None)
    i = name.rfind('.')
    pname = name[:i]
    parent = sys.modules[pname]
    return import_module(name[i+1:], name, parent)

# Save the original hooks
original_reload = builtins.reload

# Replacement for reload()
def reload(module, exclude=['sys', '__builtin__', '__main__']):
    """Recursively reload all modules used in the given module.  Optionally
    takes a list of modules to exclude from reloading.  The default exclude
    list contains sys, __main__, and __builtin__, to prevent, e.g., resetting 
    display, exception, and io hooks.
    """
    global found_now
    for i in exclude:
        found_now[i] = 1
    original_import = builtins.__import__
    builtins.__import__ = deep_import_hook    
    try:
        ret = deep_reload_hook(module)
    finally:
        builtins.__import__ = original_import
        found_now = {}
    return ret

# Uncomment the following to automatically activate deep reloading whenever
# this module is imported
#__builtin__.reload = dreload
