Setup for cryptomodul
=====================

The concept is to have two modules which are physically separeted.

**ninja** represents the frontend, the package imported by the dev

**ninja-hidden** represents the backend imported by the frontend

The Backend handles all the keymanagment and is the decode/encode backbone

The frontend makes convenience function at disposal

Example(Linux):
---------------

Your app is running under user 'webapps'

- **EASY WAY**
    - create a hidden dir in /home/webapps, for example /home/user/webapps/.ninja
    - copy the package 'ninja-hidden' to that folder
    - make that folder only accessible to the user it runs (chmod 700)
    - include the path to your env (bashrc, profile)


- *OTHER(Better?) WAY*
    - create a new user, with no login, no ssh-login, for example **pysec**
    - create a home folder and inside it create a hidden folder

    for example:/home/pysec/.hidden

    - copy 'ninja-hidden' to that folder

- *PERMISSIONS*
    A. Use the pysec group
        - add user webapps to the pysec group
        - a set permissions to
            - full access to the user :7
            - ro acces to the group:   4
            - no rights for others:    0
            - chmod -R 740 /home/pysec/.hidden

    B. Use a new group
        - create a new group for ex. 'local'
        - add user webapps to the 'local' group
        - sudo chown -R pysec.local /home/pysec/.hidden (to change the group ownership)
        - sudo chmod -R 740 /home/pysec/.hidden


Fingerprint generation:
=======================
_randomize:

    - takes the original key
    - randomizes it
    - outputs randomized key:str & passphrase:list

_randomize2:
    - takes the randomized token:str & passphrase:list from _randomize
    - turns token into a list, and adds a rndm char BEFORE the original char
    - adds a rndm char BEFORE the original char in the passphrase
    - extends the token list with the passphrase list

_fingerprinting:


How to cypher
=============

1. login -> user:Email-Adress, pwd
2. take username from email,username,domain,salt
3. Generate control string: @pwd@salt@domain

    - This way we only need to change the hash on pwd lost

4. Generate control hash from 3. and check against db
5. If true, generate control string: @username@email@salt
6. Generate ky with ky from strings func

    - Breakpoint for email loss

7. Check if key is authorized, should return 1/2 key
8. Decode second 1/2 key
9. Generate the user key
10. Return the key object


Tables cypher
=============

**User**

|    col     |   encryption |
|------------|--------------|
|   username |  SHA256      |
|   pwd      |  SHA256      |


**user_settings:**

|    col     |   encryption |
|------------|--------------|
|credentials |  userkey     |
| links      |  userkey     |
-----------------------------


**calendars:**

|    col     |   encryption |
|------------|--------------|
|    name    |  userkey     |
|description |  userkey     |
|   location |  userkey     |
-----------------------------




