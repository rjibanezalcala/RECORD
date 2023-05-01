# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 13:28:42 2023
Last updated 
v0.0.0

@author: Raquel Ibáñez Alcalá

The serendipity.py library allows easy connections to a PostgreSQL database
through a Python interface.

"""

# PostgreSQL connection
import psycopg2 as sql
# Config parser for database connection
from configparser import ConfigParser as cfgp

class Serendipity:
    def __init__(self):
        self.conn = None
        self.curr = None
        self.conn_params = None
    
    def parse_ini(self, filename='serendipity_lib/bin/config.ini',
                  section='postgresql'):
        # Create a parser
        parser = cfgp()
        # Read config file
        parser.read(filename)

        # Find the appropriate section, defaults to postgresql
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))

        return db
    
    def without_keys(self, d, keys):
        return {x: d[x] for x in d if x not in keys}
    
    def connect(self, credentials='serendipity_lib/bin/config.ini'):
        """ Connect to the PostgreSQL database server """
        self.conn = None
        try:
            # Read connection parameters from .ini file
            self.conn_params = self.parse_ini(filename=credentials, section='postgresql')
    
            # Connect to the PostgreSQL server
            print('\n  Attempting to connect to PostgreSQL database...')
            invalid = {}
            self.conn = sql.connect(**self.without_keys(self.conn_params, invalid))
    		
            # Create a cursor that will act as a mailbox between this code and
            # the server responses
            self.curr = self.conn.cursor()
            
            return True
           
        except (Exception, sql.DatabaseError) as error:
            # Print error if there is a connection error.
            print(error)
            return False
    
    def get_version(self):
        try:
            # Execute a test statement
            print('\n  Requesting database version from server...')
            print('\n  PostgreSQL database version:')
            self.curr.execute('SELECT version()')
    
            # Display the PostgreSQL database server version
            db_version = self.curr.fetchone()
            print(' ','[SERVER]', db_version)
            
            return True
        
        except (Exception, sql.DatabaseError) as error:
            # Print error if there is a connection error.
            print(error)
            
            return False
    
    def exists(self, dest_table):
        print("\n  Checking if table '"+dest_table+"' exists...")
        
        # Build query
        query = "SELECT EXISTS ("\
                + "SELECT FROM "\
                + "pg_tables "\
                + "WHERE "\
                + "schemaname = 'public' AND "\
                + "tablename  = '"+dest_table+"'"\
                + ");"
        
        # Execute query
        self.curr.execute(query)
        
        # Response should only have one line, fetch one "row".
        resp = self.curr.fetchone()
        
        if resp[0]:
            print("  Destination table '"+dest_table+"' exists!")
        else:
            print("  Destination table '"+dest_table+"' does not exist.")
            
        return resp[0]
    
    def query_database(self, query):
        try:
            # Execute query
            self.curr.execute(query)
            # Fetch all results
            raw_data = self.curr.fetchall()
            # Check if anything came back
            if raw_data:
                # Create a list of keys from the table headers in the database
                keys = [i[0] for i in self.curr.description]
                # And prepare to parse the data.
                data_row = dict()
                data_table = list()
                row_index = 0
                # cell_index = 0
                # Place all fetched rows into list of dictionaries
                for row in raw_data: # For each row fetched...
                    for i,item in enumerate(row): # Then for each item in the row...
                        # Update the row dictionary with a key/value pair using the list of keys created before
                        data_row.update({keys[i]: item})
                        # Then move on to the next item
                        # cell_index += 1
                    # When done with this row, append the resulting dictionary to the list
                    data_table.append(data_row)
                    # Then empty the row dictionary
                    data_row = dict()
                    # And move on to the next row
                    row_index += 1
                    
                return data_table
            
            else:
                # If no results, return nothing
                return None
        
        except (Exception, sql.DatabaseError) as error:
            print("\nQuery did not complete successfully.\n"+str(error))
            
            return False
        
    def execute_query(self, query):
        try:
            # Execute query
            self.curr.execute(query)
            
            return True
        except (Exception, sql.DatabaseError) as error:
            print("\nQuery did not execute successfully.\n"+str(error))
            
            return False
                
    def disconnect(self):
        # Close the communication with the PostgreSQL database
        self.curr.close()

        if self.conn is not None:
            self.conn.close()
            print('\nDatabase connection closed.')
        else:
            print('\nNo database connection to close.')
            
    # def create_table(self, table_name, **kwargs):
    #     # Parse input
    #     col_str = ""
    #     for key, value in kwargs.items():
    #         # {column name} {sql data type} {column constraint}
    #         col_str += "{0} {1}, ".format(key, type(value))
        
    #     # Build an SQL query to create the desired table if (and only if) it
    #     # doesn't exist.
    #     query = "CREATE TABLE IF NOT EXISTS"\
    #             + table_name + " ("\
    #             + "id INT(nextval('livetable2_id_seq'::regclass)) NOT NULL"\
    #             + col_str + ");"

    #     self.cur.execute()