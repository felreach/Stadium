/////////////////
Info
/////////////////
Description: Pokemon tournament game
Created by: 
Felreach - www.twitch.tv/felreach
Version: 1.0.5

/////////////////
Installation
/////////////////
0. Make sure you have the 2.7.13 Python downloaded and hooked to the Streamlabs chatbot.
	0a. Heres the link: https://www.python.org/downloads/release/python-2713/ (the x86/32bit version is recommended(no x64/64bit version)).
	0b. Install the python.
	0c. In Global Script Settings (Scripts tab) select the folder for Python Directory.
	0d. Navigate to Python 2.7.13 Lib folder (the selected path should look something like: C:\Program Files (x86)\Python\Python27\Lib").
1. On the Github repository page click "Clone or download" button and select download zip button.
2. Open the Streamlabs chatbot and go into Scripts tab.
3. Click the Import button and select the downloaded .zip file.
4. I recommend going through the settings and saving them.
5. Make sure the script is enabled. (little checkbox next to it in the listed scripts)
6. The script should announce itself into the twitch chat when its loaded.

note: if you're upgrading from an earlier version check all of the settings that they are set correctly and save them (even if you didn't change any setting)

/////////////////
Description
/////////////////
Users enter the tournament by using !stadium [type] command where type is substituted with any of the following Pokemon types.
Allowed types: normal, fighting, flying, poison, ground, rock, bug, ghost, steel, fire, water, grass, electric, psychic, ice, dragon, dark, fairy
Then a tournament is created in which users fight their way to the finals battle by battle (the tournament can be made to progress faster by using a PerRound setting). The tournament announces the results into chat.

The chosen type matters for the battles. The winning probabilities depend on which type of Pokemon meet in the battle. Those are based on table from bulbapedia ( https://bulbapedia.bulbagarden.net/wiki/Type ).
Winner of the tournament receives a prize in form of chat currency (script can be set to use external currency by providing a command and giving the bot appropriate permissions to use the command)

Commands (using default command):
!stadium [validType] - for entering the tournament
!stadium random - enter the tournament with random type
!stadium [types OR listtypes] - lists available Pokemon types
!stadium commands - lists available commands
!stadium info - displays basic (read useless) information about the script

Manager Commands:
!stadium [start] - forcibly starts the tournament if there are any Trainers which entered
!stadium [prepare OR readyup] - opens the Stadium when its locked/closed or prepares it when its on cooldown
!stadium [lock] - locks the stadium

/////////////////
Notes
/////////////////
- external command for payout doesn't seem to work

/////////////////
Version History
/////////////////
1.0.5:
 - added !stadium trainers command
 - allowed streamer/moderators to use !stadium reset so they have more control over the tournament
 - disabled !stadium start when the tournament is cooling down
 - added option for displaying the type trainers are using when battling
 - fixed payout using internal currency (NotLikeThis)
1.0.4:
 - minor fixes
1.0.3:
 - !stadium has a response now
 - added command !stadium lock 
 - status command displays little bit more info now
1.0.2:
 - Fixed failure of my English
 - Listing types now mentions the random option
1.0.1:
 - Added periodic messages about tournament sign up and relevant settings for this feature
 - Script now announces itself when loaded
 - Changed payout message when payout is disabled
 - Maybe some other minor cosmetic changes
 - Allowed trainers to enter with random type
1.0.0:
 - First Release version for testing

/////////////////
(c) Copyright
/////////////////
Felreach - www.twitch.tv/felreach | https://twitter.com/Felreach
All rights reserved. You may edit the files for personal use only.
