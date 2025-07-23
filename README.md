
# Agie

![A image depicting the bot's profile on Discord, showing its banner and main avatar image. The banner is a black and white image with chess pieces while the avatar is a girl with pink hair holding a deck of cards - she is memorizing it.](/static/agie.png)

> About the bot:

This bot is an extension of a bigger project, and it is meant to interact with our Discord community but also enhance the experience of our software <a href=https://github.com/andersonmemory/Magil>Magil</a>. Here is a brief description of the aforementioned software:

> Magil, Mágil or just Mente Ágil, is a software designed for mentathletes for training and doing online competitions regarding memory tasks such as memorizing a deck of cards, names and faces, digits and other disciplines.

> Technologies used: <a href=https://www.python.org/>Python</a>, <a href=https://pycord.dev/>Pycord</a> and <a href=https://mariadb.org/>MariaDB</a>.

## Table of Contents
- [Installation](#Installation)
- [Usage](#Usage)
- [Discord server](#Discord)

## Installation
Execute the _install.sh_ file:
```
$ chmod +x install.sh
$ ./install.sh
```

Install the python packages:
```
$ pip install -r requirements.txt
```

Setting up the Mariadb database:
```
$ mariadb -u root -p
Enter password: *enter your password*
MariaDB [(none)]> create database magil_ecosystem;
exit;
```
Cloning the database:
```
$ mariadb -u root -p magil_ecosystem < starting_database.sql
```
Fill the envinronment variables inside your ```.env``` file that was automatically created after the execution of ```install.sh```. Insert ```BOT_TOKEN``` with your Discord bot token (<a href=https://guide.pycord.dev/getting-started/creating-your-first-bot>see this guide page if you don't have one yet</a>), ```DB_USER``` and ```DB_PASSWORD``` with your mariadb user and password.

### Run the bot.
Do ```python run.py``` and now in the Discord server, use the command ```/get_members``` to populate your database containing Discord users on the server you are in.
![a](/static/get_members.png)

> Now you're done!

## Usage
Run the main file
```
$ python run.py
```

## Discord

If you would like to contribute by giving suggestions or even to help with the code, feel free to join us on our Discord server using this <a href=https://discord.com/invite/eenrGd2jhg>invite link</a>. 