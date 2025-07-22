.. _commands_page:

List of all commands currently available
==============================================

.. Add warning for advice to turn off server owner and moderation commands for everyone, using Discord specific server settings panel for this.

.. warning::

    Don't forget to turn off server owner and moderation commands for everyone, by using Discord specific server settings panel for this.

    Add overrides by going to:
    Server settings > Apps > Integrations > Agie


User level commands
-------------------

**/pomodoro:** allows to customize pomodoro duration for short and long break, as well as customize colors and add a custom gif image to break's image.
OBS: currently, it also enables you to customize stopwatch color.

**/rank:**  allows to visualize a rank with memberws who focused more in VC.

**/grafico:** generates a visual graph for focused hours and can compare with other members' data.

**/foco:** shows your focus status, including your study streak info.

**/number** <inicial> <final>: provides a random number between two numbers. Useful for randomly choosing your own mind palace.


Moderation level commands
-------------------------

**/ban** <@member> <reason>:  bans specified member. It requires a password from the moderator in order to work.

**/warn** <@member> <reason>: warns specified member. It requires a password from the moderator in order to work.

Server owner level commands
---------------------------

**/get_members:** fills the database with all members in order to populate it. Useful if its the first time the bot joined or discord_users table is empty.

**/add_admin** <@member> <password>: adds specified member to the moderators table, creating its own unique password associated with, protected by hashing algorithms (bcrypt).


