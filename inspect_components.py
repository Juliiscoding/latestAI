#!/usr/bin/env python
"""
Inspection script for examining the ETL components built.
This script displays information about the components without requiring database connections.
"""
import os
import sys
import inspect
from pprint import pprint
import importlib

def inspect_class(cls):
    """Inspect a class and print its attributes and methods."""
    print(f"\n{'='*80}")
    print(f"CLASS: {cls.__name__}")
    print(f"{'='*80}")
    
    # Print docstring
    if cls.__doc__:
        print(f"\nDOCSTRING:\n{cls.__doc__.strip()}")
    
    # Print attributes (class variables)
    class_attrs = {name: value for name, value in cls.__dict__.items() 
                  if not name.startswith('__') and not callable(value)}
    if class_attrs:
        print("\nCLASS ATTRIBUTES:")
        for name, value in class_attrs.items():
            print(f"  {name}: {value}")
    
    # Print methods
    methods = {name: func for name, func in cls.__dict__.items() 
              if callable(func) and not name.startswith('__')}
    if methods:
        print("\nMETHODS:")
        for name, func in methods.items():
            signature = inspect.signature(func)
            print(f"  {name}{signature}")
            if func.__doc__:
                doc_lines = func.__doc__.strip().split('\n')
                if len(doc_lines) > 1:
                    print(f"    {doc_lines[0].strip()}")
                else:
                    print(f"    {func.__doc__.strip()}")

def inspect_module(module_name):
    """Inspect a module and print information about its classes."""
    try:
        module = importlib.import_module(module_name)
        print(f"\n{'#'*100}")
        print(f"MODULE: {module_name}")
        print(f"{'#'*100}")
        
        if module.__doc__:
            print(f"\nMODULE DOCSTRING:\n{module.__doc__.strip()}")
        
        # Find all classes in the module
        classes = {name: cls for name, cls in inspect.getmembers(module, inspect.isclass) 
                  if cls.__module__ == module.__name__}
        
        if not classes:
            print("\nNo classes found in this module.")
            return
        
        print(f"\nFound {len(classes)} classes:")
        for name in classes:
            print(f"  - {name}")
        
        # Inspect each class
        for name, cls in classes.items():
            inspect_class(cls)
            
    except ImportError as e:
        print(f"Error importing module {module_name}: {e}")
    except Exception as e:
        print(f"Error inspecting module {module_name}: {e}")

def main():
    """Main function to inspect ETL components."""
    print("Inspecting ETL Components\n")
    
    # List of modules to inspect
    modules = [
        # Transformers
        "etl.transformers.base_transformer",
        "etl.transformers.supplier_transformer",
        
        # Models
        "etl.models.aggregations",
        "etl.models.data_warehouse",
        
        # Data Mart
        "etl.data_mart"
    ]
    
    for module_name in modules:
        inspect_module(module_name)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
