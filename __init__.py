#!/bin/python3
"""
The income reporter is a graphical shell for recording Bitcoin based income
for use with the Lab-93 borkerage system.

It offers three fields for recording the dollar amount recieved, the equivalent
amount in satoshis, and the price of Bitcoin at the time of receipt.
"""


import tkinter
from tkinter import messagebox
from subprocess import run
from datetime import datetime, timedelta
from os import getlogin as user
from argparse import ArgumentParser

from Lab93DatabaseSystem.submodules.DatabaseAPI import SQLite3


def RuntimeFunctionality(database: str=f"/home/{user()}/.local/database/finance.db"):
    """
    """

    WEEKLY = None
    DAILY = None
    WEEKEND = None
    FRIDAY = None

    # Create the directory for the database if it doesn't exist.
    run(f"mkdir --parents {'/'.join(database.split('/')[0:-1])}".split())


    ''' Date-Time References
    Here we get the dating algorithms squared away; we need to define todays
    date, and what day of the week that is.  With that established we just
    count backwards to Sunday, and then add 6 days to that for Saturday.

    Take note of days off and optional work days; those days get flagged
    as either weekends or Fridays.  Never ask for hours worked on a day off,
    and ask if we worked on Friday before we assume we did.

    After establiishing the start and end dates for a Sunday through Saturday
    pay period we concatentate them together for an easily typable PayPeriod.
    The PayPeriod object
    '''
    # Set todays current date.
    today       = datetime.today()
    day_of_week = today.weekday()
    date = datetime.strftime( today, "%Y-%m-%d" )

    # Set weekend and friday flags for daily functionality.
    if day_of_week == 5: WEEKEND = True; FRIDAY = True
    elif day_of_week == 6: WEEKEND = True

    # Calculate the range of dates todays date falls between.
    sunday   = today  - timedelta( days=( day_of_week + 1 ) )
    saturday = sunday + timedelta( days=6 )

    # Format those dates as a YYYY-MM-DD time string.
    week_start = datetime.strftime( sunday,   "%Y-%m-%d" )
    week_end   = datetime.strftime( saturday, "%Y-%m-%d" )

    # Create the PayPeriod object by appending the end to the start.
    PayPeriod = f"{week_start}:{week_end}"


    ''' Database Checks
    Given the supplied sqlite3.db filepath as a valid database, check for
    an existing scheme that matches our programs needs.  There must be a table
    for tracking `income` and a table for `hours`.  If either of these tables
    does not exist they are to be created.

        [income table]:
               date            |  dollar  |  satoshi  |  bitcoin
    1). 2023-04-24:2023-05-01  |  $23.53  |  3393474  |  0.00039
    2). 2023-05-02:2023-05-08  |  $45.48  |  3838232  |  0.00123

                               ... .... ...

        [hours table]:
               date     |  clockin  |  clockout
            2023-05-01  |  2257hrs  |  0720hrs
            2023-05-02  |  2230hrs  |  0728hrs

                               ... .... ...
    '''
    # NOTE: [Income Table] configuration.
    # If the database already exists, do nothing. Otherwise;
    if SQLite3.checkTable(  database, "income" ) > 0:
        # Check for an existing entry for the current pay period.
        if len( SQLite3.selectRow( database,
                                   "income",
                                   "date",
                                   str(PayPeriod) ) ) > 0:

            # If input has been given then flag WEEKLY as true.
            messagebox.showinfo( title="Weekly Income",
                                 message=( f"You have already "
                                           f"filled out your "
                                           f"weekly income." )  )
        else: collectIncome(database, PayPeriod)

    else:
        SQLite3.newTable(  database, "income", "date",    "TEXT" )
        SQLite3.newColumn( database, "income", "dollar",  "REAL" )
        SQLite3.newColumn( database, "income", "satoshi", "REAL" )
        SQLite3.newColumn( database, "income", "bitcoin", "REAL" )


    # NOTE: [Hours Table] configuration.
    # Create the hours table if it doesn't exist.
    if SQLite3.checkTable(  database, "hours" ) > 0:
        if len( SQLite3.selectRow( database,
                                  "hours",
                                  "date",
                                  str(date) ) ) > 0:

            messagebox.showinfo( title="Daily Hours",
                                 message=( f"You have already "
                                           f"filled out your "
                                           f"daily hours." )   )
        else: collectHours(database, date)

    else: # Create a new hours table for the user.
        SQLite3.newTable(  database, "hours", "date",      "TEXT" )
        SQLite3.newColumn( database, "hours", "clockin",   "TEXT" )
        SQLite3.newColumn( database, "hours", "clockout",  "TEXT" )


    exit()


    ''' Application level variables and constants. '''
def collectHours(database, period):
    window = tkinter.Tk()
    window.title("Lab-93 Hours Reporting Tool")


    hours = [str(x).rjust(2, '0') for x in range(0, 24)]
    minutes = [str(x).rjust(2, '0') for x in range(0, 60)]

    clockinHour    = tkinter.StringVar(); clockinHour.set( "00"    )
    clockinMinute  = tkinter.StringVar(); clockinMinute.set( "00"  )
    clockoutHour   = tkinter.StringVar(); clockoutHour.set( "00"   )
    clockoutMinute = tkinter.StringVar(); clockoutMinute.set( "00" )


    def submit():
        while True:
            clockin = f"{clockinHour.get()}{clockinMinute.get()}"
            clockout = f"{clockoutHour.get()}{clockinMinute.get()}"
            finished = True; break

        if finished:
            if messagebox.askyesno( title="Confirm Submission",
                                    message=( f"You are about to enter:"
                                              f"\nClock-In:  {clockin}"
                                              f"\nClcok-Out: {clockout}"
                                              f"\n\nIs this correct?" )  ):

                SQLite3.new_uniqueRow( database, 
                                        "hours", 
                                        "date, clockin, clockout",
                                        f"'{period}', {clockin}, {clockout}" )

                window.destroy()


    # Display the current date being tracked.
    # NOTE: Most of the hours being tracked are for the
    # current date; however the day actually starts the
    # date before.
    dateLabel     = tkinter.Label( text=f"{period}"   )
    dateLabel.grid( row=0, column=1 )

    # Label the hours column for the clockin and clockout rows.
    hourLabel     = tkinter.Label( text="Hours"     )
    hourLabel.grid(row=2, column=1)

    # Label the minute column for clockin/clockout.
    minuteLabel   = tkinter.Label( text="Minutes"   )
    minuteLabel.grid(row=2, column=2)

    # Label the row as describing the clock in time.
    clockinLabel  = tkinter.Label( text="Clock-In"  )
    clockinLabel.grid(row=3, column=0)

    # Label the row as describing clock out.
    clockoutLabel = tkinter.Label( text="Clock-Out" )
    clockoutLabel.grid(row=4, column=0)

    # Drop-Down menu for the clockin hour.
    clockin_hour = tkinter.OptionMenu(window, clockinHour, *hours)
    clockin_hour.grid(row=3, column=1)

    # Menu selection for clockin minutes.
    clockin_minute = tkinter.OptionMenu(window, clockinMinute, *minutes)
    clockin_minute.grid(row=3, column=2)

    # Drop-Down for clockin hour.
    clockout_hour = tkinter.OptionMenu(window, clockoutHour, *hours)
    clockout_hour.grid(row=4, column=1)

    # Menu for minutes.
    clockout_minute = tkinter.OptionMenu(window, clockoutMinute, *minutes)
    clockout_minute.grid(row=4, column=2)

    # Add a button to call the submit() function.
    submit_button = tkinter.Button( text="Submit", command=submit )
    submit_button.grid(             row=4, column=3               )
    


    return  window.mainloop()


def collectIncome(database, period):
    # Set mainloop window and it's configurations.
    window =                             tkinter.Tk()
    window.title(    "Lab-93 Income Reporting Tool" )

    # Set buffers for containing input values.
    dollar_amount  = tkinter.StringVar()
    satoshi_amount = tkinter.StringVar()
    bitcoin_price  = tkinter.StringVar()


    ''' Program executive functionality.'''
    def submit():
        """
        Retrieve entry values as numbers and write them to the financial
        database.
        """
        
        while True:
            try:
                dollar   = float( dollar_amount.get()  )
                satoshi  = int(   satoshi_amount.get() )
                bitcoin  = float( bitcoin_price.get()  ); finished = True
                break

            except ValueError:
                messagebox.showwarning( title="Input Error", 
                                        message="Error! Please only type a number." )
                dollar_amount.set(  "" )
                satoshi_amount.set( "" )
                bitcoin_price.set(  "" ); finished = False
                break

        if finished:
            if messagebox.askyesno( title="Confirm Submission",
                                    message=( f"You are about to enter:"
                                              f"\nDollar Amount: ${str(dollar)}"
                                              f"\nSatoshi Amount: {str(satoshi)}"
                                              f"\nBitcoin Amount: {str(bitcoin)}"
                                              f"\n\nIs this correct?" )   ):

                SQLite3.new_uniqueRow( database, 
                                       "income", 
                                       "date, dollar, satoshi, bitcoin",
                                       f"'{period}', {dollar}, {satoshi}, {bitcoin}" )

                window.destroy()


    
    # Add a row for listing total dollars earned.
    dollarAmount_Label = tkinter.Label( text="Dollar Amount:"      )
    dollarAmount_Label.grid(            row=1, column=0            )
    dollarAmount = tkinter.Entry(       textvariable=dollar_amount )
    dollarAmount.grid(                  row=1, column=2            )
    
    # Add a row for equating those dollars to satoshis.
    satoshiAmount_Label = tkinter.Label( text="Satoshi Amount:"      )
    satoshiAmount_Label.grid(            row=2, column=0             )
    satoshiAmount = tkinter.Entry(       textvariable=satoshi_amount )
    satoshiAmount.grid(                  row=2, column=2             )
    
    # Add a row for tracking btc price buy-in.
    bitcoinPrice_Label = tkinter.Label( text="Bitcoin Price:"      )
    bitcoinPrice_Label.grid(            row=3, column=0            )
    bitcoinPrice = tkinter.Entry(       textvariable=bitcoin_price )
    bitcoinPrice.grid(                  row=3, column=2            )
    
    # Add a button to call the submit() function.
    submit_button = tkinter.Button( text="Submit", command=submit )
    submit_button.grid(             row=3, column=3               )
    
    
    return  window.mainloop()


if __name__ == "__main__":
    arguments = ArgumentParser()
    arguments.add_argument("-D", "--database")

    arguments = arguments.parse_args()

    if arguments.database: RuntimeFunctionality(database=arguments.database)
    else: RuntimeFunctionality()
