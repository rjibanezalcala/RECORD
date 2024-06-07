# Welcome to RECORD/python!
This folder contains all Python scripts and libraries made for the RECORD system. The code in this section was written as an alternative way to make use of the RECORD system without the need for licensed software such as [Ethovision](https://www.noldus.com/ethovision-xt). Our Python scripts are designed to be self-contained driving software for RECORD that allows it to be run in conjunction with other free, open-source software specifically for animal tracking solutions such as [Bonsai](https://open-ephys.org/bonsai), [B-SOID](https://github.com/YttriLab/B-SOID), [DeepLabCut](https://github.com/DeepLabCut/DeepLabCut), and [SLEAP](https://github.com/talmolab/sleap).

All code was written using the Spyder IDE contained within [Anaconda](https://www.anaconda.com/). 

## Dependencies
These scripts were written using a variety of packages, namely:
 1. pandas
 2. pyserial
 3. numpy
 4. random
 7. csv
 8. sys
 9. os
 10. pytz
 11. sqlalchemy
 12. glob
 13. ast
 14. dateutil.parser
 15. psycopg2
 16. configparser

## Packages
We have developed two Python packages for interfacing with the RECORD hardware and with our PostgreSQL database. They are described below.
### RECORD-lib
The RECORD-lib package is a serial communications-oriented package that helps simplify communication with the RECORD hardware through Com port communications via USB. We have included the package functions both for communication with the microcontroller, and tools for creating cutomised trials. 
### SerendiPYty
The SerendiPYty package offers functions we developed for communication with our PostgreSQL database. The name 'SerendiPYty' is a spinoff that references [our MatLab application 'Serendipity'](https://github.com/lddavila/UTEP-Brain-Computation-Lab-Remote-Databases-and-Serendipity-App/tree/main), which also interfaces with our database . The main difference is that Serendipity parses and uploads purely behavioural data coming from Ethovision XT, while SerendiPYty parses and uploads data produced by [Bonsai](https://open-ephys.org/bonsai) and our [RECORD-lib library](https://github.com/rjibanezalcala/RECORD/tree/main/python/RECORD-lib). This package offers tools for quick data handling and pre-processing, as well as for uploading said pre-processed data to the database.

> Written with [StackEdit](https://stackedit.io/).
<!--stackedit_data:
eyJoaXN0b3J5IjpbLTExNDQxMzcyNDVdfQ==
-->
