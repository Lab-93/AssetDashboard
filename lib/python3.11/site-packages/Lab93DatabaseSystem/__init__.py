#!/bin/python3
"""
The Lab-93 Database System provides a pre-built and scriptable suite of
functionality for implementing and maintaining an SQLite3 database on your
Linux system.  It is an in-house tool used for building out the back end of the
guyyatsu.me website, or even potentially re-building from a wipeout.

When called as a script from the command line, the buildAdministratorDatabase()
function will be called with or without arguments being given.  As of version
0,0.2, it initializes a .db file formatted as a Lab-93 standard tableau,
defining a credentials table and a contacts table.

The credentials table contains columns for tracking API keys from various
platforms; notably telegram, alpaca, discord, and NASA, as well as a username
to associate with these keys.  It is reccomended to use the Lab93Cryptogram
package in conjunction with maintaining assets within this table.

The contacts table lists rows of individuals by there first and last names,
which are required text strings.  Other associated methods of contact
information include the persons email, phone, github, or their own
personal website.  In the future, it is planned to allow the end user to add
new and unique columns to this table provided they do not conflict with the
schema.
"""


''' In-House framework for interacting with database objects. '''
from .submodules.DatabaseAPI import SQLite3


def buildAdministratorDatabase( database: str="./sqlite3.db", **config ):
    """
    The buildAdministratorDatabase function requires a string, `database`,
    that defines a path to a .db file, and an optional config dictionary.

    Each key in this dictionary refers to a table to be created within the
    .db file; and each of these contains in turn two more nested dictionaries.
    These describe the default column and its type along with any extra
    columns desired, as well as their data types.

    For every key specifically associated with a column or table, the key
    itself is understood to also be the 'name' of the object.  For example,
    the dictionary index `config["credentials"]["username"] = "TEXT"` implies
    that the `username` column of othe `credentials` table accepts input of
    the type `TEXT.`
    """

    # Default configuration for the Lab-93 database system used by
    # other in-house software kits.
    #
    # Each key in the dict represents a table within the database,
    # and contains the metadata to configure the setup to suit
    # our needs.
    if not config:
        config = { "credentials": { "username": "TEXT",

                                    "columns":  { "telegram_admin": "BYTES",
                                                  "alpaca_key":     "BYTES",
                                                  "alpaca_secret":  "BYTES",
                                                },
                                  },

                   "contacts": { "first_name": "REQUIRED TEXT",

                                 "columns": { "last_name":     "REQUIRED TEXT",
                                              "email_address": "TEXT",
                                              "phone_number":  "TEXT",
                                              "github":        "TEXT",
                                              "website":       "TEXT",
                                            },
                               },
                 }

    # Iterate through every top-level key and validate it's existence.
    #NOTE:
    ''' Each key must also be a dictionary containing:

            1.  - A key representing the name of the default column within the
                  table, with a value describing it's SQLite3 datatype.

            2.  - A 'columns' key that is ALSO a dictionary who's keys function
                  exactly the same as the first key, with the key itself
                  describing the column name and the value stating the type.
    '''
    for table in config.keys():

        # If the table exists;
        if SQLite3.checkTable( database, 
                               table=str(table) ) > 0: print(
            f"  --{str(table).title()} table exists."
        )

        # If the table does not exist;
        else:

            ''' The first key in the table dict is the default column. '''
            default_column = [ column for column in config[table].keys() ][0]

            ''' Plug the string value of the key into the SQLite3.newTable
            function, along with the table string. '''
            SQLite3.newTable( database,
                              table=str(table),
                              column=str(default_column),
                              column_type=config[table][default_column] ); print(
                f"  --{str(table).title()} table created."
            )


        # Iterate through the columns dictionary inside the table dictionary.
        for column in config[table]["columns"].keys():

            # If the column exists;
            if SQLite3.checkColumn( database,
                                    table=str(table),
                                    column=str(column)) > 0: print(
                f"    --{str(column).title()} column exists."
            )

            # If the column does not exist;
            else:
                column_type = config[table]["columns"][column]
                SQLite3.newColumn( database,
                                   table=str(table),
                                   column=str(column),
                                   column_type=column_type, ); print(
                    f"    --{str(column).title()} column created."
                )
