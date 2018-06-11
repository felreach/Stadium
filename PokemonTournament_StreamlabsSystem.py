#---------------------------------------
#	Import Libraries
#---------------------------------------
import clr
import sys
import json
import os
import random
import ctypes
import threading
import time
import codecs

#---------------------------------------
#	[Required]	Script Information
#---------------------------------------
debuggingMode = True
ScriptName = "Tournament - Pokemon"
Website = "https://twitter.com/Felreach"
Description = "Tournament - Pokemon"
Creator = "Felreach"
Version = "1.0.0"

#---------------------------------------
#	Classes
#---------------------------------------
class Fighter:

	def __init__(self):
		self.name = None
		self.deckType = None
		self.currentWinnings = 0
		return 

	def __init__(self, twitchname, type, winnings):
		self.name = twitchname
		self.deckType = type
		self.currentWinnings = winnings
		return 
	

class Match:

	def __init__(self,childMatch1, childMatch2, depth):
		self.previousMatchTop = childMatch1 # stored as ID
		self.previousMatchBot = childMatch2 # stored as ID
		self.nextMatch = None
		self.trainerTop = None
		self.trainerBot = None
		self.winner = None
		self.looser = None
		self.remainingProgression = 1
		self.hasProgressed = False
		self.depth = depth
		return 




#---------------------------------------
#	Set Variables
#---------------------------------------
configFile = "TournamentConfig.json"
settings = {}
user = ""

RandomInstance = random.SystemRandom()
randomNames = ["Salty", "Monday", "Briana", "Blossom", "Lucilla", "Dorris", "Elia", "Lisbeth", "Esther", "Angila", "Roger", "Particia", "Lilia", "Tabetha", "Leopoldo", "Lanny", "Elene", "Anton", "Demetrius", "Von", "Raymond", "Amie", "Sharlene", "Vickey", "Kandace", "Darrel", "Jayson", "Bonita", "Nicolette", "Mendy", "Carson", "Ouida"]

tickCounter = 0

#tournament data
stadiumLocked = False
tournamentOpened = False
tournamentStarted = False
tournamentReady = True
enteredTrainers = []
allTrainers = []
allMatches = []
tournamentDepth = -1
currentProgressionDepth = -1
startBracket = []
currentTick = ""


#command params
cmdParamListTypes = {"types", "listtypes"}
cmdParamReadyTourny = {"prepare", "readyup"}
cmdParamStartTourny = {"start"}


#battle defs
TYPES = ["normal", "fighting", "flying", "poison", "ground", "rock", "bug", "ghost", "steel", "fire", "water", "grass", "electric", "psychic", "ice", "dragon", "dark", "fairy"]
INEFFECTIVE_AGAINST = { "normal" : {"ghost"}, "fighting" : {"ghost"}, "poison" : {"steel"}, "ground" : {"flying"}, "ghost" : {"normal"}, "electric" : {"ground"}, "psychic" : {"dark"}, "dragon" : {"fairy"}}
WEAK_AGAINST = { "normal" : {"rock", "steel"}, "fighting" : {"flying", "poison", "bug", "psychic", "fairy"}, "flying": {"rock", "steel", "electric"}, "poison" : {"poison", "ground", "rock", "ghost"}, "ground" : {"bug", "grass"}, "rock" : {"fighting", "ground", "steel"}, "bug": {"fighting", "flying", "poison", "ghost", "steel", "fire", "fairy"}, "ghost" : {"dark"}, "steel" : {"steel", "fire", "water", "electric"}, "fire" : {"rock", "fire", "water", "dragon"}, "water" : {"water", "grass", "dragon"}, "grass" : {"flying", "poison", "bug", "steel", "fire", "grass", "dragon"}, "electric" : {"grass", "electric", "dragon"}, "psychic" : {"steel", "psychic"}, "ice" : {"steel", "fire", "water", "ice"}, "dragon" : {"steel"}, "dark" : {"fighting", "dark", "fairy"}, "fairy" : {"poison", "steel", "fire"}}
STRONG_AGAINST = { "fighting" : {"normal", "rock", "steel", "ice", "dark"}, "flying" : {"fighting", "bug", "grass"}, "poison": {"grass"}, "ground" : {"poison", "rock", "steel", "fire", "electric"}, "rock" : {"flying", "bug", "fire", "ice"}, "bug" :{"grass", "psychic", "dark"}, "ghost" : {"ghost", "psychic"}, "steel" : {"rock", "ice", "fairy"}, "fire" : {"bug", "steel", "grass", "ice"}, "water": {"ground", "rock", "fire"}, "grass" : {"ground", "rock", "water"}, "electric" : {"flying", "water"}, "psychic" : {"fighting", "poison"}, "ice" : {"flying", "ground", "grass", "dragon"}, "dragon" : {"dragon"}, "dark" : {"ghost", "psychic"}, "fairy" : {"fighting", "dragon", "dark"}}
ineffectiveStrength = 10.0
weakStrength = 25.0
evenStrength = 50.0
strongStrength = 75.0


#threads
threadsKeepAlive = True
entranceLockTimerThreadActive = False
startPauseTimerThreadActive = False
tournamentTimerThreadActive = False
cooldownTimerThreadActive = False

#---------------------------------------
#	Def functions
#---------------------------------------

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def GetBattleDuration(ours, against, isFinals = False):
	if ours == None or against == None:
		return 1
	
	result1 = GetStrength(ours, against)
	result2 = GetStrength(against, ours)

	r = 1
	if result1 == "strong":
		if result2 == "strong":
			r = 1
		elif result2 == "even":
			r = 1
		elif result2 == "weak":
			r = 1
		elif result2 == "ineffective":
			r = 1
	if result1 == "even":
		if result2 == "strong":
			r = 1
		elif result2 == "even":
			r = 2
		elif result2 == "weak":
			r = 2
		elif result2 == "ineffective":
			r = 2
	if result1 == "weak":
		if result2 == "strong":
			r = 1
		elif result2 == "even":
			r = 2
		elif result2 == "weak":
			r = 3
		elif result2 == "ineffective":
			r = 4
	if result1 == "ineffective":
		if result2 == "strong":
			r = 1
		elif result2 == "even":
			r = 2
		elif result2 == "weak":
			r = 4
		elif result2 == "ineffective":
			r = 5
	
	if isFinals == True:
		r = max(4, 2 * r)

	return r

def GetStrength(ours, against):
	if(ours in TYPES):
		if(against in TYPES):
			if(STRONG_AGAINST.has_key(ours)):
				if(against in STRONG_AGAINST[ours]):
					return "strong"
			if(WEAK_AGAINST.has_key(ours)):
				if(against in WEAK_AGAINST[ours]):
					return "weak"
			if(INEFFECTIVE_AGAINST.has_key(ours)):
				if(against in INEFFECTIVE_AGAINST[ours]):
					return "ineffective"
	return "even"

def GetStrengthValue(ours, against):
	if(ours in TYPES):
		if(against in TYPES):
			if(STRONG_AGAINST.has_key(ours)):
				if(against in STRONG_AGAINST[ours]):
					return strongStrength
			if(WEAK_AGAINST.has_key(ours)):
				if(against in WEAK_AGAINST[ours]):
					return weakStrength
			if(INEFFECTIVE_AGAINST.has_key(ours)):
				if(against in INEFFECTIVE_AGAINST[ours]):
					return ineffectiveStrength
	return evenStrength

def Battle(first, second):
	result = {"winner" : None, "looser" : None}
	if(first in TYPES):
		if(second in TYPES):
			strength1 = GetStrengthValue(first, second)
			strength2 = GetStrengthValue(second, first)
			toWin = strength1 / (strength1 + strength2)
			if( RandomInstance.random() < toWin):
				result["winner"] = "first"
			else :
				result["winner"] = "second"
		else:
			result["winner"] = "first"
	else:
		if(second in TYPES):
			result["winner"] = "second"

	if result["winner"] == "first":
		result["looser"] == "second"
	elif result["winner"] == "second":
		result["looser"] == "first"

	return result

def ResolveBattle(battleToResolve):
	# mark progressed
	battleToResolve.hasProgressed = True

	# quick resolve because theres isnt an opponent
	if battleToResolve.trainerTop != None and battleToResolve.trainerBot == None:
		battleToResolve.winner = battleToResolve.trainerTop
		battleToResolve.looser = None
		return battleToResolve
	
	# quick resolve because theres isnt an opponent
	if battleToResolve.trainerTop == None and battleToResolve.trainerBot != None:
		battleToResolve.winner = battleToResolve.trainerBot
		battleToResolve.looser = None
		return battleToResolve

	if battleToResolve.trainerTop == None and battleToResolve.trainerBot == None:
		battleToResolve.winner = None
		battleToResolve.looser = None
		return battleToResolve

	if battleToResolve.remainingProgression > 0:
		return battleToResolve

	# get types
	typeA = allTrainers[battleToResolve.trainerTop].deckType
	typeB = allTrainers[battleToResolve.trainerBot].deckType
	
	result = Battle(typeA, typeB)
	
	if result["winner"] == "first":
		battleToResolve.winner = battleToResolve.trainerTop
		battleToResolve.looser = battleToResolve.trainerBot
	else:
		battleToResolve.winner = battleToResolve.trainerBot
		battleToResolve.looser = battleToResolve.trainerTop

	allTrainers[battleToResolve.winner].currentWinnings += settings["PrizePerBattle"]

	return battleToResolve

def InitBracket():
	global RandomInstance
	global startBracket, allMatches, tournamentDepth, currentProgressionDepth
	
	startBracket = []
	allMatches = []
	enteredCount = len(enteredTrainers)
	if enteredCount <= 0:
		return

	# count up the leafs in the tournament tree
	startCount = 2
	tournamentDepth = 0
	while startCount < enteredCount:
		startCount *= 2
		tournamentDepth += 1

	currentProgressionDepth = tournamentDepth + 1 # set current finished depth

	Debug("start count, entered count:" + str(startCount) + "," + str(enteredCount))
	#init the brakcets
	startBracket = range(enteredCount) # map out the trainer IDs
	if startCount - enteredCount != 0:
		c = (startCount - enteredCount)
		n =[ None ] * c
		startBracket.extend(n)
	RandomInstance.shuffle(startBracket)

	Debug("filling matches:")
	#fill matches
	parentDictionary = {1 : 0, 2: 0}
	d = 0
	index = 0
	if d != tournamentDepth:
		allMatches.append(Match(childMatch1 = (index * 2+1), childMatch2 = (index * 2+2), depth = d))
	else:
		allMatches.append(Match(childMatch1 = None, childMatch2 = None, depth=d))
	
	while d < tournamentDepth:
		d += 1
		for x in range(2**d):
			index += 1
			if d != tournamentDepth:
				allMatches.append(Match(childMatch1 = index * 2+1, childMatch2 = index * 2+2, depth = d))
				parentDictionary[index * 2+1] = index
				parentDictionary[index * 2+2] = index
			else:
				allMatches.append(Match(childMatch1 = None, childMatch2 = None, depth = d))
	
	Debug("filling parents:")
	# fill parents
	index = 0
	while index < len(allMatches):
		if index in parentDictionary:
			allMatches[index].nextMatch = parentDictionary[index]
		index += 1

	Debug("filling lowest depth matches with participants:")
	# fill the participants of all the matches at the lowest depth
	start = len(allMatches) - startCount/2 #figure out where the last matches start (the tournament matches are stored as a binary heap in an array)
	index = 0
	for x in range(start, len(allMatches)):
		#x = start + y
		Debug("x: "+ str(x))
		allMatches[x].trainerTop = startBracket[index]
		allMatches[x].trainerBot = startBracket[index+1]
		# update battle duration
		type1 = None
		type2 = None
		if allMatches[x].trainerTop != None:
			type1 = allTrainers[allMatches[x].trainerTop].deckType
		if allMatches[x].trainerBot != None:
			type2 = allTrainers[allMatches[x].trainerBot].deckType
		allMatches[x].remainingProgression = GetBattleDuration(type1, type2)
		index += 2

	if len(enteredTrainers) <= 2 and len(enteredTrainers) > 0:
		allMatches[0].remainingProgression = GetBattleDuration(type1, type2, True)

	return

def advanceWinner(currentMatch):
	global allMatches
	next = allMatches[currentMatch].nextMatch 
	if next != None:
		if currentMatch == allMatches[next].previousMatchTop:
			allMatches[next].trainerTop = allMatches[currentMatch].winner
		if currentMatch == allMatches[next].previousMatchBot:
			allMatches[next].trainerBot = allMatches[currentMatch].winner

	allMatches[next].remainingProgression = 1
	if allMatches[next].trainerTop != None and allMatches[next].trainerBot != None:
		type1 = allTrainers[allMatches[next].trainerTop].deckType
		type2 = allTrainers[allMatches[next].trainerBot].deckType
		if next == 0: # we are going into finals, use longer duration
			allMatches[next].remainingProgression = GetBattleDuration(type1, type2, True)
		else:
			allMatches[next].remainingProgression = GetBattleDuration(type1, type2)

	return

def advanceTournament():
	global allMatches, currentProgressionDepth
	
	Debug("advancing tournament")
	result = {"IsFinalBattle" : False, "Battles" : [], "AdvancementStyle" : settings["AdvancementStyle"], "Winners": [], "Loosers" : []}
	
	result["AdvancementStyle"] = settings["AdvancementStyle"]

	# search for max depth
	i = len(allMatches) - 1
	maxDepth = -1
	while i >= 0:
		if allMatches[i].remainingProgression > 0:
			maxDepth = max(allMatches[i].depth, maxDepth)
		i -= 1

	Debug("advanceTournament() max depth:" + str(maxDepth))
	currentProgressionDepth = maxDepth + 1
	# this is last battle
	if maxDepth == 0: 
		Debug("advanceTournament() final battle:")
		result["IsFinalBattle"] = True
		result["BattleHasProgressed"] = allMatches[0].hasProgressed

		if allMatches[0].remainingProgression > 0 and settings["FinalsStyle"] == "Long":
			allMatches[0].remainingProgression -= 1
			allMatches[0].hasProgressed = True
		elif allMatches[0].remainingProgression > 0 and settings["FinalsStyle"] == "Short":
			allMatches[0].remainingProgression = 0
			allMatches[0].hasProgressed = True

		if allMatches[0].remainingProgression == 0:
			currentProgressionDepth = 0
			allMatches[0] = ResolveBattle(allMatches[0])
			# no need to update parent here, this is last battle

		result["Winners"].append(allMatches[0].winner)
		result["Loosers"].append(allMatches[0].looser)
		result["Battles"].append(allMatches[0])

		return result

	# PER ROUND
	if settings["AdvancementStyle"] == "PerRound":
		Debug("advanceTournament() per round:")
		i = len(allMatches) - 1
		while i >= 0:
			if allMatches[i].remainingProgression > 0 and allMatches[i].depth == maxDepth:
				allMatches[i].remainingProgression = 0
				allMatches[i].hasProgressed = True
				allMatches[i] = ResolveBattle(allMatches[i])
				advanceWinner(i)
				
				# pass winners into the next battles
				result["Winners"].append(allMatches[i].winner)
				result["Loosers"].append(allMatches[i].looser)
				result["Battles"].append(allMatches[i])
				pass 
			i -= 1

	# PER BATTLE
	if settings["AdvancementStyle"] == "PerBattle":
		Debug("advanceTournament() per battle:")
		i = len(allMatches) - 1
		
		# find first match we can advance
		while i >= 0:
			if allMatches[i].remainingProgression > 0:
				if settings["BattleStyle"] == "Long":
					allMatches[i].remainingProgression -= 1
				elif settings["BattleStyle"] == "Short":
					allMatches[i].remainingProgression = 0

				Debug("advancing match-remaining progression: " + str(allMatches[i].remainingProgression))
				result["BattleHasProgressed"] = allMatches[i].hasProgressed

				allMatches[i].hasProgressed = True
				# resolve battle
				if allMatches[i].remainingProgression == 0:
					allMatches[i] = ResolveBattle(allMatches[i])
					advanceWinner(i)

				break
			i -= 1

		result["Winners"].append(allMatches[i].winner)
		result["Loosers"].append(allMatches[i].looser)
		result["Battles"].append(allMatches[i])

	# update currentProgressionDepth
	i = len(allMatches) - 1
	maxDepth = -1
	while i >= 0:
		if allMatches[i].remainingProgression > 0:
			maxDepth = max(allMatches[i].depth, maxDepth)
		i -= 1

	currentProgressionDepth = maxDepth + 1

	return result


def startEntranceLockTimer():
	global settings, currentTick
	Debug("startEntranceLockTimer() called")

	currentTick = "EntranceLock"

	return

def EntranceLockTimerThread():
	global entranceLockTimerThreadActive
	
	entranceLockTimerThreadActive = True
	remaining = settings["TournamentSignUpPeriod"]

	if remaining > 0:
		while remaining > 0 and entranceLockTimerThreadActive and threadsKeepAlive:
			if remaining % 60 == 0 or remaining == 30 or remaining == 10:
				s = "Tournament sign up ends in " + str(remaining) + " seconds."
				SendMsg(s)
			Debug("EntranceLockTimerThread() tick")
			remaining -= 1
			time.sleep(1)	

	if not entranceLockTimerThreadActive : #this would mean we were cancelled from the outside so we need to do some cleanup

		return

	entranceLockTimerThreadActive = False
	startTournament()
	return

def startTournament():
	global tournamentOpened, tournamentStarted, currentTick, entranceLockTimerThreadActive

	tournamentStarted = True
	Debug("startTournament()")
	entranceLockTimerThreadActive = False
	currentTick = "StartPause"

	return

def StartPauseTimerThread():
	global startPauseTimerThreadActive, currentTick

	startPauseTimerThreadActive = True
	currentTime = 0

	while currentTime < 10 and startPauseTimerThreadActive and threadsKeepAlive:
		Debug("StartPauseTimerThread() tick")
		currentTime += 1
		time.sleep(1)	

	if not startPauseTimerThreadActive : #this would mean we were cancelled from the outside so we need to do some cleanup

		return

	InitBracket()

	Debug("end of start pause thread")
	currentTick = "Tournament"
	startPauseTimerThreadActive = False
	return

def TournamentTimerThread():
	global tournamentTimerThreadActive

	tournamentTimerThreadActive = True
	currentTime = 0
	timerDuration = settings["PauseBetweenRounds"]
	dontSkip = settings["PauseBetweenRounds"] > 0
	if currentProgressionDepth == 1:
		timerDuration = settings["PauseBetweenFinalRounds"]
		dontSkip = settings["PauseBetweenFinalRounds"] > 0

	while currentTime < timerDuration and tournamentTimerThreadActive and threadsKeepAlive and dontSkip:
		Debug("TournamentTimerThread() tick")
		currentTime += 1
		time.sleep(1)	

	if not tournamentTimerThreadActive: #this would mean we were cancelled from the outside so we need to do some cleanup
		resetTournament()
		return

	tournamentTimerThreadActive = False
	return

def CooldownTimerThread():
	global cooldownTimerThreadActive 

	cooldownTimerThreadActive = True
	currentTime = 0

	while currentTime < settings["TournamentPreparationTime"] and cooldownTimerThreadActive and threadsKeepAlive:
		currentTime += 1
		time.sleep(1)

	if not cooldownTimerThreadActive: #this would mean we were cancelled from the outside so we need to do some cleanup
		resetTournament()
		return

	resetTournament()
	s = "Stadium is ready to host another tournament! Use " + str(settings["Command"]) + " <pokemon type> to enter."
	SendMsg(s)

	cooldownTimerThreadActive = False
	return


def finishTournament():
	global tournamentOpened, tournamentStarted, tournamentReady

	tournamentOpened = False
	tournamentStarted = False
	tournamentReady = False

	cooldownTournament()

	return

def cooldownTournament():
	global currentTick, tournamentOpened, tournamentReady, tournamentStarted

	currentTick = "Cooldown"

	return

#hard resets the tournament, also tells all the threads to stop
def resetTournament(unlock = False):
	global stadiumLocked, tournamentReady, tournamentOpened, tournamentStarted, currentTick
	global enteredTrainers, allTrainers, currentBracket, startBracket, currentProgressionDepth, tournamentDepth, allMatches

	global entranceLockTimerThreadActive, startPauseTimerThreadActive, tournamentTimerThreadActive, cooldownTimerThreadActive

	currentTick = ""
	tournamentReady = True
	tournamentOpened = False
	tournamentStarted = False

	stadiumLocked = settings["StadiumStartsLocked"]
	if unlock:
		stadiumLocked = False

	enteredTrainers = []
	allTrainers = []
	currentBracket = []
	startBracket = []
	allMatches = []
	currentProgressionDepth = -1
	tournamentDepth = -1

	entranceLockTimerThreadActive = False
	startPauseTimerThreadActive = False
	tournamentTimerThreadActive = False
	cooldownTimerThreadActive = False

	return

def getBattleStatus():
	result = "Battles: "
	
	if len(allMatches) > 0:
		for i in range(len(allMatches)):
			result += str(i) + "-["
			result += "Next:" + str(allMatches[i].nextMatch) + " "
			result += "PrevTop:" + str(allMatches[i].previousMatchTop) + " "
			result += "PrevBot:" + str(allMatches[i].previousMatchBot) + " "
			result += "Trainers:" + str(allMatches[i].trainerTop) + "|" + str(allMatches[i].trainerBot) + " "

			result += "],"

	return result

def getTournamentStatus():
	activeThread = "None"
	if entranceLockTimerThreadActive:
		activeThread = "entrance lock"
	if startPauseTimerThreadActive: 
		activeThread = "start pause"
	if tournamentTimerThreadActive:
		activeThread = "tournament"
	if cooldownTimerThreadActive:
		activeThread = "cooldown"


	result = "Tournament Status: "
	result += "Locked: " + str(stadiumLocked) + " ; "
	result += "Ready: " + str(tournamentReady) + " ; "
	result += "Opened: " + str(tournamentOpened) + " ; "
	result += "Started: " + str(tournamentStarted) + " ; "
	result += "Tournament depth current/total:" + str(currentProgressionDepth) + "/" + str(tournamentDepth) + " ; "
	result += "Matches count: " + str(len(allMatches)) + " ; "
	result += "BattleStyle: " + settings["BattleStyle"] + " ; "
	result += "ActiveThread: " + activeThread + " ; "

	return result

def ScriptToggled(state):
	global threadsKeepAlive
	# if enabled again tell the script to keep the threads running again
	if state:
		threadsKeepAlive = True
	# if the script gets disabled, stop all timers and resets the textfiles
	else:
		resetTournament()
		
		ResetUptime()
		timerData["twitchApiResponseOffline"] = 0
		Unload()
	return

def Unload():
    global threadsKeepAlive
    threadsKeepAlive = False
    return


def Debug(message):
    if debuggingMode:
        Parent.Log("PokemonTournament", message)


def SendMsg(message):
	if message == "":
		return
	if settings["PrefaceMessages"] == True:
		message = "Stadium: " + message
	Parent.SendTwitchMessage(message)
	return

#---------------------------------------
#	[Required] Intialize Data (Only called on Load)
#---------------------------------------
def Init():
	global settings, configFile, RandomInstance
	global stadiumLocked, ineffectiveStrength, weakStrength, evenStrength, strongStrength

	RandomInstance = random.SystemRandom()

	path = os.path.dirname(__file__)
	try:
		with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
			settings = json.load(file, encoding='utf-8-sig')
	except:
		settings = {
			"OnlyWhenLive": False,
			"Command": "!stadium",
			"Permission": "Everyone",
			"ManagerPermission": "Moderator",
			"AllowRegularsToManage" : False,
			"EntryCost": 0,
			"UseCommonResponses" : True,
			"EnableInvalidTypeResponse" : True,
			"EnableEntryResponse" : True,
			"EnableEntryCostResponse" : True,
			"EnablePayout" : False,
			"PrizePerBattle": 5,
			"FinalPrizePerTrainer": 5,
			"FinalPrize": 200,
			"CurrencyName" : "of Chat Currency",
			"UseExternalPayout" : False,
			"ExternalPayoutCommand" : "!addpoints $user $amount",
			"UtilityCooldown": 5,
			"TypeIneffectiveValue" : 20,
			"TypeWeakValue" : 40,
			"TypeEvenValue" : 50,
			"TypeStrongValue" : 70,
			"ResultAnnoucementStyle" : "Loosers",
			"PrefaceMessages" : False,
			"OnCooldownResponse": "$user, the command is still on cooldown for $cd seconds!",
			"OnUserCooldownResponse": "$user the command is still on user cooldown for $cd seconds!",
			"StadiumStartsLocked" : False,
			"AdvancementStyle" : "PerRound",
			"BattleStyle": "Long",
			"FinalsStyle": "Long",
			"TournamentSignUpPeriod" : 120,
			"PauseBetweenRounds" : 20,
			"PauseBetweenFinalRounds" : 15,
			"TournamentPreparationTime" : 120,
			"BackdoorForFel" : True
		}

	stadiumLocked = settings["StadiumStartsLocked"]

	ineffectiveStrength = settings["TypeIneffectiveValue"]
	weakStrength = settings["TypeWeakValue"]
	evenStrength = settings["TypeEvenValue"]
	strongStrength = settings["TypeStrongValue"]


	return


#---------------------------------------
#	[Required] Execute Data / Process Messages
#---------------------------------------
def Execute(data):
	global user
	global tournamentOpened, tournamentReady, tournamentStarted
	global enteredTrainers, allTrainers
	global RandomInstance

	if data.IsChatMessage():
		Debug("processing msg")
		user = data.User			
		FelOverride = user.lower() == "felreach" and settings["BackdoorForFel"] == True
		tempResponseString = ""

		if (data.GetParam(0).lower() == settings["Command"]):
			# skip the command when stream isnt live
			if settings["OnlyWhenLive"] and not Parent.IsLive():
				SendMsg("The Stadium cannot be used because the stream isn't live!")
				return

			hasPermission = Parent.HasPermission(data.User, settings["Permission"], "")
			hasManagePermission = Parent.HasPermission(data.User, settings["ManagerPermission"], "")
			if settings["AllowRegularsToManage"]:
				hasManagePermission = hasManagePermission or Parent.HasPermission(data.User, "Regular", "")

			if FelOverride:
				hasPermission = True
				hasManagePermission = True

			# OPEN STADIUM
			if(data.GetParam(1).lower() in cmdParamReadyTourny and hasManagePermission):
				if stadiumLocked:
					resetTournament(True)
					tempResponseString = "Stadium has been unlocked and is ready for next tournament! Sign up with " + settings["Command"] + " [type]!"
				else:
					if not tournamentReady and not tournamentOpened and not tournamentStarted:
						resetTournament(True)
						tempResponseString = "All of the tournament staff and organizers went super saiyan and prepared the stadium for the next Tournament!"
					else:
						if tournamentStarted:
							tempResponseString = "Tournament is already already under way @$user!"
						elif tournamentOpened:
							tempResponseString = "Tournament is already opened!"
						elif tournamentReady:
							tempResponseString = "Tournament is ready! No need for cleaning or additional preparations."
			# START 
			elif(data.GetParam(1).lower() in cmdParamStartTourny and hasManagePermission):
				if not stadiumLocked:
					if len(enteredTrainers) > 0 and not tournamentStarted:
						tempResponseString = "Starting the tournament!"
						startTournament();
					else:
						tempResponseString = "There are no participants ready for the tournament!"
				else:
					tempResponseString = "Stadium is currently locked."
			# STATUS
			elif data.GetParam(1).lower() == "status" and FelOverride:
				tempResponseString = getTournamentStatus()

			# BATTLE STATUS
			elif data.GetParam(1).lower() == "battlestatus" and FelOverride:
				# @todo switch to whisper?
				tempResponseString = getBattleStatus()

			# RESET
			elif data.GetParam(1).lower() == "reset" and FelOverride:
				resetTournament()
				tempResponseString = "@$user is hard resetting the tournament!"

			# INFO
			elif data.GetParam(1).lower() == "commands" and hasPermission:
				if settings["UtilityCooldown"] > 0 and Parent.IsOnCooldown(ScriptName, "UtilityCooldownCommands"):
					pass
				else:
					# list the commands
					s = "Available Commands: "
					s += "types OR listtypes, "
					s += "commands, info"
					s += "; Manager Commands: "
					s += "start, "
					s += "prepare OR readyup "
					tempResponseString = s
					if settings["UtilityCooldown"] > 0:
						Parent.AddCooldown(ScriptName, "UtilityCooldownCommands", settings["UtilityCooldown"])

			# INFO
			elif data.GetParam(1).lower() == "info" and hasPermission:
				# check for cooldown
				if settings["UtilityCooldown"] > 0 and Parent.IsOnCooldown(ScriptName, "UtilityCooldownInfo"):
					pass
				else:
					tempResponseString = "Script " + "[" + ScriptName + "]" + " version:" + Version + " made by: " + Creator
					if settings["UtilityCooldown"] > 0:
						Parent.AddCooldown(ScriptName, "UtilityCooldownInfo", settings["UtilityCooldown"])

			# ADDNPC
			elif (data.GetParam(1).lower() == "addnpc" or data.GetParam(1).lower() == "addnpcs") and FelOverride:
				count = 1
				if RepresentsInt(data.GetParam(2)):
					count = int(data.GetParam(2))
					if count < 0:
						count = 0
				if not stadiumLocked:
					if tournamentReady and not tournamentStarted:
						typeoverride = ""
						t = data.GetParam(3).lower()
						if t in TYPES:
							typeoverride = t

						for x in range(count):
							npc = RandomInstance.choice(randomNames)
							npc += "NPC"
							type = RandomInstance.choice(TYPES)

							if typeoverride != "":
								type = typeoverride

							enteredTrainers.append(npc)
							allTrainers.append(Fighter(npc, type, 0))

							if tournamentOpened:
								tempResponseString = "Entering $npc into the tournament with " + type + " type Pokemon!"
							if not tournamentOpened:
								tournamentOpened = True
										
								randomType = RandomInstance.choice(TYPES)
								randomType = str.capitalize(randomType)
								tempResponseString = "$npc enters the pokemon stadium to claim the " + randomType + " Badge. "
								tempResponseString += "Is there anyone willing to challenge them?"

							tempResponseString = tempResponseString.replace("$npc", npc)
							SendMsg(tempResponseString)

						startEntranceLockTimer()
						tempResponseString = ""

					else:
						tempResponseString = "Can't enter a random NPC into the tournament."
				else:
					tempResponseString = "Can't enter a random NPC into the tournament. The stadium is locked."

			# LIST TYPES
			elif(data.GetParam(1).lower() in cmdParamListTypes and hasPermission):
				if settings["UtilityCooldown"] > 0 and Parent.IsOnCooldown(ScriptName, "TypesUtilityCooldown"):
					pass
				else:
					tempResponseString = str(TYPES)
					tempResponseString = tempResponseString.replace("[","")
					tempResponseString = tempResponseString.replace("]","")
					tempResponseString = tempResponseString.replace("\'","")
					tempResponseString = "You can enter the tournament with either of these pokemon types: " + tempResponseString
					if settings["UtilityCooldown"] > 0:
						Parent.AddCooldown(ScriptName, "TypesUtilityCooldown", settings["UtilityCooldown"])

			# JOIN TOURNY AS A USER
			elif data.GetParamCount() == 2 and hasPermission: #we have exactly two params, that means the second one should be a type
				# @todo how to subtract points when they are external?
				entryprice = settings["EntryCost"]
				
				# check locked
				if not stadiumLocked:
					# check ready
					if tournamentReady:
						# check started
						if not tournamentStarted:
							if user not in enteredTrainers:
								type = data.GetParam(1).lower()
								if type in TYPES:
									if entryprice <= Parent.GetPoints(data.User): # use param for the price
										enteredTrainers.append(user)
										allTrainers.append(Fighter(user, type, 0))

										if tournamentOpened:
											if settings["EnableEntryResponse"]:
												tempResponseString = "Entering @$user into the tournament with " + type + " type Pokemon!"
										if not tournamentOpened:
											tournamentOpened = True
										
											tempResponseString = "@$user with " + type + " type Pokemon enters the Stadium to claim the Badge! "
											tempResponseString += "Is there anyone willing to challenge them?"

										startEntranceLockTimer()
									else:
										if settings["UseCommonResponses"] and settings["EnableEntryCostResponse"]:
											# @todo a case when external points are used?
											tempResponseString = ""
								else:
									if settings["UseCommonResponses"] and settings["EnableInvalidTypeResponse"]:
										tempResponseString = "@$user ! " + data.GetParam(1) + " is an invalid Pokemon type!"
							else:
								if settings["UseCommonResponses"]:
									tempResponseString = "@$user already entered the tournament."
						else:
							if settings["UseCommonResponses"]:
								tempResponseString = "@$user you are too late. The tournament is already under way."
								# slowpoke msg
								if RandomInstance.random() < 0.05:
									tempResponseString = "@$user is a Slowpoke. Kappa The tournament is already under way."
								pass
					else:
						if settings["UseCommonResponses"]:
							# theres a cooldown 
							if settings["UtilityCooldown"] > 0 and Parent.IsOnCooldown(ScriptName, "StadiumUtilityCooldown"):
								pass
							else:
								tempResponseString = "The stadium is currently being cleaned and repaired for the upcoming tournament."
								if settings["UtilityCooldown"] > 0:
									Parent.AddCooldown(ScriptName, "StadiumUtilityCooldown", settings["UtilityCooldown"])

				elif stadiumLocked:
					tempResponseString = "The stadium is locked."

		# RANDOM TEST
		if (data.GetParam(0).lower() == "!randomtest" and FelOverride):
			tempResponseString = "random counts: "

			counts = {}
			for x in range(0, len(TYPES)):
			    counts[x] = 0

			m = 0
			for x in range(0, 10000):
				r = RandomInstance.random()
				m = max(r,m)
				val = int(r * len(TYPES))
				counts[val] += 1

			for x in counts.keys():
				tempResponseString += str(x) + "-" + str(counts[x]) + "; "

			tempResponseString += " max:" + str(m)
		# REF TEST
		if (data.GetParam(0).lower() == "!reftest" and FelOverride):
			tempResponseString = "ref test: "

			array1 = ["0","1","2","4"]
			array2 = ["5", "6"]
			array2.append(array1[0])

			tempResponseString += str(array1) + " " + str(array2)
			tempResponseString += " => "
			array1[0] = "x"
			tempResponseString += str(array1) + " " + str(array2)

		tempResponseString = tempResponseString.replace("$user", user)
		SendMsg(tempResponseString)
	return

#---------------------------------------
# Reload Settings on Save
#---------------------------------------
def ReloadSettings(jsonData):
	global settings, configFile

	Init()


	return

def OpenReadMe():
    location = os.path.join(os.path.dirname(__file__), "ReadMe.txt")
    os.startfile(location)
    return

#---------------------------------------
#	[Required] Tick Function
#---------------------------------------
def Tick():
	global currentTick, tickCounter, RandomInstance

	if tickCounter % 100 == 0:
		Debug("Tick:" + currentTick)
	tickCounter += 1

	if tournamentOpened and not tournamentStarted:
		#tick entrance lock 
		if currentTick == "EntranceLock" and not entranceLockTimerThreadActive:
			s = "The tournament sign up period begins now! Pokemon Trainers! You have $time seconds to sign up!"
			s = s.replace("$time", str(settings["TournamentSignUpPeriod"]))
			SendMsg(s)
			Debug("starting entrance lock timer")
			threading.Thread(target=EntranceLockTimerThread, args=()).start()

	if tournamentStarted:
		#tick pause before tourny start
		if currentTick == "StartPause" and not startPauseTimerThreadActive:
			# if only one trainer entered, finish the tournament 
			if len(enteredTrainers) == 1:
				s0 = "Only @" + enteredTrainers[0] + " signed up for the tournament. Sadly for them, no reward will be paid out because that would be too easy."
				s1 = "After waiting in the lobby for " + str(1+RandomInstance.randint(1,9))  + " hours, @" + enteredTrainers[0] + " leaves the Stadium empty handed as staff refused to award anything to them for being the only trainer to show up."
				s2 = "@" + enteredTrainers[0] + " grumpily leaves the Stadium as there was one else to challenge."
				s = RandomInstance.choice([s0, s1, s2]);
				SendMsg(s)
				currentTick = "TournamentFinish"
			else:
				#announce tournament started
				s = str(len(enteredTrainers)) + " trainers have signed up for the tournament. There's a future champion among them, but nobody knows who it will be. "
				s += "We will soon find out! The tournament staff announces the start! "
				s += "The stadium closes, the stands rumble with cheering and the first challengers for the Badge enter the Stadium's arena."
				SendMsg(s)
				threading.Thread(target=StartPauseTimerThread, args=()).start()

		#tick tournament advancement
		if currentTick == "Tournament" and not tournamentTimerThreadActive:
			#process current round
			result = advanceTournament()
			
			# if we are close to the Final match we broadcast each individual match (based on a setting)
			if result["IsFinalBattle"] == True:
				s = ""
				battle = result["Battles"][0]
				Debug("Final battle has progressed: " + str(battle.hasProgressed ) + " " + str(battle.remainingProgression))
				if battle.remainingProgression > 0 and result["BattleHasProgressed"] == False:
					s0 = "The final battle is here! @$trainer1 and @$trainer2 will fight for the Badge."
					s1 = "@$trainer1 and @$trainer2 are about to meet in the finals!"
					s2 = "@$trainer1 and @$trainer2 are about to duke it out for the Badge!"
					s = RandomInstance.choice([s0, s1])
				elif battle.remainingProgression == 0 and settings["FinalsStyle"] == "Short":
					s = "In the finals, @$winner wins against @$looser."
				elif battle.remainingProgression >= 1:
					Debug("Tick: final battle progressing")
					s0 = "The battle is fierce! The finalists are using all of the tricks they learned on their journey of becoming the best pokemon trainer."
					s1 = "@$trainer1 is putting on a lot of pressure but @$trainer2 is keeping up!"
					s2 = "@$trainer2 is putting on a lot of pressure but @$trainer1 is keeping up!"
					s3 = "It's not looking good for @$trainer1, they are falling behind while being on the defensive!"
					s4 = "It's not looking good for @$trainer2, they are falling behind while being on the defensive!"
					s5 = "Both trainers pulled back. They are preparing for the next exchange of attacks!"
					s = RandomInstance.choice([s0, s1, s2, s3, s4, s5])
				elif battle.remainingProgression == 0:
					s0 = "Amazing! After a serious exchange @$winner manages to overpower their oponent and finish them off."
					s1 = "Amazing! At the last second @$winner's Pokemon pulls off an amazing move against $looser and wins."
					s2 = "At last, @$winner finds a crack in @$looser's defenses and deals them a finishing blow."
					s = RandomInstance.choice([s0, s1, s2])

				# replace tags
				s = s.replace("$trainer1", allTrainers[battle.trainerTop].name)
				s = s.replace("$trainer2", allTrainers[battle.trainerBot].name)
				if battle.winner != None:
					s = s.replace("$winner", allTrainers[battle.winner].name)
					s = s.replace("$type", str(allTrainers[battle.winner].deckType).capitalize())
				if battle.looser != None:
					s = s.replace("$looser", allTrainers[battle.looser].name)

				SendMsg(s)
			else:
				# if we go match by match
				if settings["AdvancementStyle"] == "PerBattle":
					s = ""
					battle = result["Battles"][0]
					if battle.trainerTop != None and battle.trainerBot != None:
						if battle.remainingProgression > 0 and result["BattleHasProgressed"] == False:
							s = "The match between @$trainer1 and @$trainer2 is underway"
						elif battle.remainingProgression >= 1:
							s = "@$trainer1 and @$trainer2 are going at it."
						elif battle.remainingProgression == 0:
							s0 = "@$winner wins the battle against @$looser."
							s1 = "In the end @$winner wins convincingly against @$looser."
							s2 = "In a close match @$winner bests @$looser."
							s = RandomInstance.choice([s0, s1])
							s = s.replace("$winner", allTrainers[battle.winner].name)
							s = s.replace("$looser", allTrainers[battle.looser].name)

						s = s.replace("$trainer1", allTrainers[battle.trainerTop].name)
						s = s.replace("$trainer2", allTrainers[battle.trainerBot].name)

						SendMsg(s)
					else:
						trainer = ""
						if battle.trainerTop == None and battle.trainerBot != None:
							trainer = allTrainers[battle.trainerBot].name
						if battle.trainerTop != None and battle.trainerBot == None:
							trainer = allTrainers[battle.trainerTop].name

						if trainer != "":
							s = trainer + " has no opponent for this battle, they advance by default."

						SendMsg(s)

				elif settings["AdvancementStyle"] == "PerRound": # if we go be entire round
					s = ""
					addedWinners = False
					if settings["ResultAnnoucementStyle"] == "Winners" or settings["ResultAnnoucementStyle"] == "Both":
						s = "Another round of battles is finished. "
						addedWinners = True
						
						# get all the winners
						winners = []
						for i in range(len(result["Battles"])):
							if result["Battles"][i].winner != None:
								winners.append(allTrainers[result["Battles"][i].winner].name)
							pass
						
						if len(winners) > 0:
							s += "Trainers progressing to the next round are: "

							for j in range(len(winners)):
								s += winners[j]
								if j != (len(winners) - 1):
									s += ", "

						else:
							s = "No Trainers are progressing into the next round."

						SendMsg(s)
					if settings["ResultAnnoucementStyle"] == "Loosers" or settings["ResultAnnoucementStyle"] == "Both":
						if addedWinners:
							s = ""
						else:
							s = "Another round of battles is finished. "

						# get all the loosers
						loosers = []
						for i in range(len(result["Battles"])):
							if result["Battles"][i].looser != None:
								loosers.append(allTrainers[result["Battles"][i].looser].name)
							pass

						if len(loosers) > 0:
							s += "Trainers knocked out of the tournament are: "

							for j in range(len(loosers)):
								s += loosers[j]
								if j != (len(loosers) - 1):
									s += ", "

						else:
							s = "No Trainers lost this round."

						SendMsg(s)

			#if tournament isnt finished launch timer to wait for next rounds
			if currentProgressionDepth > 0:
				threading.Thread(target=TournamentTimerThread, args=()).start()
			else:
				currentTick = "TournamentFinish"

		if currentTick == "TournamentFinish":
			if len(enteredTrainers) > 1:
				battle = allMatches[0]
				winnings = allTrainers[battle.winner].currentWinnings
				winnings += settings["FinalPrizePerTrainer"] * len(enteredTrainers)
				winnings += settings["FinalPrize"]

				#announce winners
				s = "The tournament is over, @$winner wins with $type Pokemon. The Badge is theirs. Their winnings are $amount $currency!"
				s = s.replace("$winner", allTrainers[battle.winner].name)
				s = s.replace("$type", str(allTrainers[battle.winner].deckType).capitalize())
				s = s.replace("$amount", str(winnings))
				s = s.replace("$currency", settings["CurrencyName"])
				SendMsg(s)
				
				if settings["EnablePayout"] == True:
					# pay out winners
					if settings["UseExternalPayout"]:
						s = settings["ExternalPayoutCommand"]
						s = s.replace("$user", allTrainers[battle.winner].name)
						s = s.replace("$amount", str(winnings))
						Parent.SendTwitchMessage(s)
					else: # pay out with internal currency
						Parent.AddPoints(user, winnings)

			SendMsg("The Stadium closes...")
			finishTournament();
		#tick post tourny cooldown
		if currentTick == "Cooldown" and not cooldownTimerThreadActive:
			threading.Thread(target=CooldownTimerThread, args=()).start()

	return