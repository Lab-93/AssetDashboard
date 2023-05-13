#!/bin/python3
"""
A simple key: value database for fast, scriptable data-storage capabilities.

Intended to aid in creating and storing new database configurations for the
`Lab93DatabaseSystem.buildAdministratorDatabase` function.
"""

import shelve

def newLine( database: str="./.database.db",
             table: str="administrator",
             index: str="credentials",
             value: str="test_credentials"):
    """
    Create a new index within the dictionary.
    """

    with shelve.open(database) as  shelf:
        shelf = {
            str(table): {
                str(index): value
            }
        }

        print(shelf)

def readLine( database: str="./.database.db",
              table: str="administrator",
             index: str="credentials"         ):
    """
    Read the value of an index from the dictionary.
    """

    with shelve.open(database) as  shelf:
        print(shelf[table])
