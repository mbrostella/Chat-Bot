from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from random import seed, choice

### AUTHENTICATION: ASSISTANT SERVICE OBJECT
authenticator = IAMAuthenticator('sixJBMkotIRp1V4D4iz_ZeYbmYsFXy-QQ-DF1diX5HIY') # replace with API key
assistant = AssistantV2(
    version = '2020-09-24',
    authenticator = authenticator
)
assistant.set_service_url('https://api.eu-gb.assistant.watson.cloud.ibm.com')
assistant_id = 'a4be8694-0066-4be7-a091-49793fac27c1' # replace with assistant ID

### FUNCTIONS

def returnEntities (response, entitiesList):
    #Makes a list of all entities detected in the answer and appends that list to the global entities list.
    entities=[]
    for i in range(len(response['output']['entities'])):
        entities.append(response['output']['entities'][i]['entity'])
    entitiesList.append(entities)
    return entitiesList

def assignPoints (entitiesList_clean, skillDict, points):
    totalQuestions=0
    #Count all non empty answers
    for answer in entitiesList_clean:
        if len(answer)>0:
            totalQuestions=totalQuestions+1
    totalPointsAssigned=0
    #Takes the entities list generated during the test, the skill dictionary and the total number of points to distribute
    #and returns the skill dictionary with the corresponding points on the found entities

    for skill in skillDict:
        for answer in entitiesList_clean:
            if len(answer)>0:#The answer must have some intent, otherwise we cannot calculate percentage, because we divide by zero
                skillDict[skill]=skillDict[skill]+int(answer.count(skill)/len(answer)/totalQuestions*points)
                totalPointsAssigned=totalPointsAssigned+int(answer.count(skill)/len(answer)/totalQuestions*points)
                #if int(answer.count(skill)/len(answer)/totalQuestions*points)>0:
                    #print(answer, int(answer.count(skill)/len(answer)/totalQuestions*points), ' points for ', skill)
    #print('Unasigned points: ', points-totalPointsAssigned)
    #Because of round numbers, some a few points can be unassigned. These will always be less than the number of questions
    #These points will be randomly distributed:
    if totalPointsAssigned<points:
        for point in range(points-totalPointsAssigned):
            randomSkill=choice(skillList)
            skillDict[randomSkill]=skillDict[randomSkill]+1
            #print('+1 random point for ', randomSkill)
    return skillDict

def assignRole (skillDict):
    maxValue=0
    for skill in skillDict:
        if skillDict[skill]>maxValue:
            maxValue=skillDict[skill]
            roleSkill=skill
    print('')
    print('You will be our next', roleDict[roleSkill][0])
    print(roleDict[roleSkill][1])
    print('')
    print('Points per skill: ')
    print(skillDict)
    print('HINT: ')
    print(roleDict[roleSkill][2])

### INITIALIZED VARIABLES

entitiesList=[]

points=150

skillList=['WeaponsSmallGuns',
           'Dialogue',
           'Medicine',
           'Negotiate',
           'Repair',
           'Science',
           'Sneak',
           'UnarmedCombat',
           'WeaponsBigGuns',
           'WeaponsShortRange']
 
skillDict={
    'WeaponsSmallGuns':9,
    'Dialogue':9,
    'Medicine':9,
    'Negotiate':9,
    'Repair':9,
    'Science':9,
    'Sneak':9,
    'UnarmedCombat':9,
    'WeaponsBigGuns':9,
    'WeaponsShortRange':9}

roleDict={
    'WeaponsSmallGuns':["Tattoo artist","Huh. I wonder who will be brave enough to be your first customer as the vault's new Tattoo Artist? I promise it won t be me.", "Try to keep the distance with your enemies and be careful not to run out of ammo"],
    'Dialog':["Marriage counselor", "Wow. Wow. Says here you're going to be the vault's Marriage Counselor. Almost makes me want to get married, just to be able to avail myself of your services.", "Speak to everyone you meet and explore all your dialogue options, that will save you a lot of fighting"],
    'Medicine':["Clinical test subject", "Interesting. 'Clinical Test Subject'... sounds like something you should excel at. I guess you and Dr. Henry will be working together.", "Use your knowledge on medicine to craft better drugs which can enhance your other skills"],
    'Negociate':["Vault chaplain","They say the G.O.A.T never lies. According to this, you're slated to be the next vault ... Chaplain. God help us all", "Collect and sell every item you find in order to buy the most powerful equipment"],
    'Repair':["Jukebox technician","Thank goodness. We're finally getting a new Jukebox Technician. That thing hasn't worked right since old Joe Palmer passed.", "Modify your equipment to obtain its maximum power"],
    'Science':["Pip-Boy programmer","Well, well. Pip-Boy Programmer, eh? Stanley will finally have someone to talk shop with.", "Your knowledge will allow you to go around risky situations, keep reading every book and magazine you can find to master other skills"],
    'sneak':["Shift supervisor","Apparently you're management material. You're going to be trained as a Shift Supervisor. Could I be talking to the next Overseer? Stranger things have happened.", "Avoid confronting enemies directly and if necessary be sure you give the first strike"],
    'UnarmedCombat':["Little league coach","I always thought you'd have a career in professional sports. You're the new vault Little League coach! Congratulations.", "Find some good armour and work on your speed to be able to strike your objectives"],
    'WeaponsBigGuns':["Laundry cannon operator","Well according to this, you're in line to be trained as a laundry cannon operator. First time for everything indeed.", "Find the strongest weapons and manage the ammunition carefully"],
    'WeaponsShortRange':["Fry cook","Looks like the diner's going to get a new Fry Cook. I'll just say this once: hold the mustard, extra pickles. Ha ha ha.", "Find some good armour and work on your speed to be able to strike your objectives"],
}

### PROGRAM

## Initialize with empty message to start the conversation.

message_input = {
    'message_type:': 'text',
    'text': ''
    }
context = {}

while message_input['text'] != 'quit':
    
## Send message to assistant.
    response = assistant.message_stateless(
        assistant_id,
        input = message_input,
        context = context
    ).get_result()

    context = response['context']

## Intent detection

    if response['output']['intents']:
        #print('Detected intent: #' + response['output']['intents'][0]['intent'])
        variableResponse=response           

## Response and Result: Print the output from dialogue, if any. Supports only a single text response.

    if response['output']['generic']:
        if response['output']['generic'][0]['response_type'] == 'text':
            print(response['output']['generic'][0]['text']) #Watson's answer.
        if len(response['output']['generic'])>1:
            print (response['output']['generic'][1]['text']) #For some reason, jupyter doesn't display the next question, so this had to be added.
        #Update EntitiesList
            entitiesList=returnEntities(response, entitiesList)
            #print(entitiesList)

## Final Results

        if len(response['output']['generic'])>1:
            if response['output']['generic'][1]['text']=='Good work! You have finished the test. Let me process your results...':
                #Answer from last question gets duplicated, so remove it
                entitiesList.pop(-1)
                entitiesList_clean=returnEntities(response, entitiesList)
                assignPoints(entitiesList_clean, skillDict, points)
                assignRole(skillDict)
            
## Prompt for next round of input: User's Answer
    
    user_input = input('>>')
    message_input = {
        'text': user_input
    }