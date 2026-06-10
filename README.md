##important##
- It is highly suggested to copy this entire folder to your local machine and run the application. 
- If you have run the older version before, keep a copy of any csv files outside this application folder. Whenever a new version is run for the first time, it will replace the current-month csv file 

#Note for versions
- v2.4 has been updated to modify MTR from MTRC for MTR receiver. When FDCT is selected as receiver, cyberupdate@soc2.cmt.net will be selected automatically. 
- v.23 has been updated to create csv files in the current folder to record all input data for each month.

Create "mail_list" folder in the current directory where the application is located and keep all txt files that include email lists
 - News Generator folder
  -----mail_list 
  -----News_Generator_v1.exe

Create "pop_mail" folder in the current directory where the application is located
 - pop_mail folder should have a txt file that includes a list of pop email list

Create "pop_config.json" and add all pop email lists 

Note for mail_list folder 
 - make sure each email moves to a new line, rather than using this character ";" at the end of each email.


Note for cc option 
 - In Preview Mode, the previewed email will be sent to its sender, even if CC emails are entered.
 - In Confirm Mode, the cc emails will be sent too. 

Note for Excel Mode,
  - This mode only works if 'Yes' is selected in Excel Mode and 'Confirm' Mode.
  - A new csv file will be created with the current month and year (eg-May_26) if no csv file with a month and year is not found.
  - Every time the 'Send' button (with 'Confirm Mode and 'Yes' in Excel Mode) is clicked, the new record will be logged in the same-month-csv file.  
  -[Update Last Row] option, 'Yes' will update the values of all selected receviers while ignoring the values of non-selected receviers. 'No' option will do nothing. Note that this option will work only if 'Yes' from Excel is selected.   
  -[Update All Columns] option, 'No' will only update the receviers columns while 'Yes' option will update all columns including the title column. Note that this option will work only if 'Yes' from Update Last Row option is selected and 'Yes' from Excel is selected.  


Note for csv
 - when the program is running, do not leave csv file open. 
 - If the csv file is open, it cannot be updated with new records. 

****
