import discord
import os
import subprocess
import sys
from neuralintents import GenericAssistant

MODEL_NAME = 'PERRINE'

# Setup Chat bot
chatbot = GenericAssistant('intents.json', model_name=MODEL_NAME)
chatbot.train_model()
chatbot.save_model()

# Load Discord API Token from file
#ADRIAN either load from file or manually enter here/replace the loadToken() call below
def loadToken():
    TOKEN_PATH = 'token.txt'
    token = ''

    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'r') as file:
            token = file.read().replace('\n', '')
    # (if file doesn't exist, ask for it via standard input, and save it)
    else:
        token = input("Discord Token:")
        with open(TOKEN_PATH, 'w') as file:
            file.write(token)
    
    return token

# This bot requires the members and reactions intents.
#intents = discord.Intents.default()
# client = discord.Client()#intents=intents)
intents = discord.Intents.all()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

# On Startup
@client.event
async def on_ready():
    #ADRIAN This is some default stuff you can change 
    message = "I am back! Did you miss me?!".format(client)
    print(message)

    if len(sys.argv) == 1 or sys.argv[1] != '-debug':
        channel = client.get_channel(1073023569409343559)
        await channel.send(message)

# Helper functions
def fromMod(message):
    is_admin = message.author.top_role.permissions.administrator
    #is_admin = discord.utils.find(lambda r: r.name == "Admin", message.guild.roles) in message.author.roles
    is_mod = discord.utils.find(lambda r: r.name == "Moderator", message.guild.roles) in message.author.roles

    return is_admin or is_mod

# On Message
@client.event
async def on_message(message):
    username = str(message.author)
    user_message = str(message.content)
    channel = str(message.channel)
    stdchannel = client.get_channel(1073023569409343559)
    vertigo = 330428337795104778
    if message.author == client.user:
        return
    
    # [===== Debug =====] #
    if message.content.startswith("PERRINEdebug "):
        if not fromMod(message):
            await message.channel.send(f"Hahahah. Nope!")
            return

        cmd = message.content[8:]
        # [UPDATE]
        if cmd == 'update':
            try:
                process = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE)
                output = process.communicate()[0].decode("utf-8")
                await message.channel.send(f"PERRINE updated by {message.author} ```{output}```")
            except Exception as e:
                await message.channel.send(f"git pull not working :frowning: ```{e}```")
                print("git pull not working :(")
        # [RESTART]
        elif cmd == 'restart':
            await message.channel.send(f"Ok boss. Restarting now....")
            os.execv(sys.executable, ['python3'] + sys.argv)
        # [404]
        else:
            await message.channel.send(f"Don't know '{cmd}'")

    # [===== Message to Perrinebot =====] #
    if message.channel.id == 1073023569409343559 and "perrine" in message.content.lower() or client.user.mentioned_in(message):
        send_as_reply = False
        message_content = message.content.lower().replace("perrine","")

        # When pinged only with "perrinebot", reply to earlier message and delete ping
        if message.reference is not None and message_content.lower() == "perrine" and fromMod(message):
            pinged_message = message
            ref_message = await message.channel.fetch_message(message.reference.message_id)

            message = ref_message
            send_as_reply = True
            message_content = ref_message.content.lower().replace("perrine","")
            await pinged_message.delete()

        response = chatbot.request(message_content)

        if send_as_reply:
            await message.reply(response)
        else:
            await message.channel.send(response)

        return


# Start Bot
client.run(loadToken())
