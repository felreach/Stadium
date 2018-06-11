#################
Info
#################
Description: Pokemon tournament game
Created by: 
Felreach - www.twitch.tv/felreach
Version: 1.0.0

Users enter the tournament by using !stadium [type] command where type is substituted with any of the following Pokemon types.
Allowed types: normal, fighting, flying, poison, ground, rock, bug, ghost, steel, fire, water, grass, electric, psychic, ice, dragon, dark, fairy
Then a tournament is created in which users fight their way to the finals battle by battle (the tournament can be made to progress faster by using a PerRound setting). The tournament announces the results into chat.

The winning probabilities depend on which type of Pokemon meet in the battle. Those are based on table from bulbapedia ( https://bulbapedia.bulbagarden.net/wiki/Type ).
Winner of the tournament receives a prize in form of chat currency (script can be set to use external currency by providing a command and giving the bot appropriate permissions to use the command).

Commands (using default command):
!stadium [validType] - for entering the tournament
!stadium [types OR listtypes] - lists available Pokemon types
!stadium commands - lists available commands
!stadium info - displays basic (read useless) information about the script

Manager Commands:
!stadium [start] - forcibly starts the tournament if there are any Trainers which entered
!stadium [prepare OR readyup] - opens the Stadium when its closed or prepares it when its on cooldown


###############
Version History
###############
1.0.0:
 - First Release version for testing

###############
(c) Copyright
###############
Felreach - www.twitch.tv/felreach | https://twitter.com/Felreach
All rights reserved. You may edit the files for personal use only.
