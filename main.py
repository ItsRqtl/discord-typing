import asyncio,decouple;from interactions import *;client=Client(token=decouple.config("token"),intents=Intents.DEFAULT);task={}
@client.command(name="typing",description="I am typing...",options=[Option(name="nickname",description="the one who are typing is: ",type=OptionType.STRING)],default_member_permissions=Permissions.ADMINISTRATOR,dm_permission=False)
async def typing_cmd(ctx,nickname=None):
    try: task[int(ctx.guild_id)]
    except:await ctx.client.modify_self_nick_in_guild(guild_id=ctx.guild_id, nickname=nickname);await ctx.send('Starting to type...', ephemeral=True);task[int(ctx.guild_id)]=asyncio.create_task(typing(ctx.channel_id))
    else:await ctx.send('I am already typing somewhere in this guild!',ephemeral=True)
async def typing(id):
    while True:await asyncio.gather(asyncio.sleep(5), client._http.trigger_typing(channel_id=id))
@client.command(name="stop",description="Enough! Stop typing!",default_member_permissions=Permissions.ADMINISTRATOR,dm_permission=False)
async def stop(ctx):
    try:task[int(ctx.guild_id)].cancel()
    except:await ctx.send("I am not typing.",ephemeral=True)
    else:task.pop(int(ctx.guild_id));await ctx.send("Stopped typing.",ephemeral=True)
    finally:await ctx.client.modify_self_nick_in_guild(guild_id=ctx.guild_id,nickname=None)
@client.command(name="invite", description="Invite to your server!")
async def invite(ctx):await ctx.send("Invite Typing to your server!",components=Button(style=ButtonStyle.LINK,label="Click me!",url="https://discord.com/api/oauth2/authorize?client_id=991618813856591942&permissions=67111936&scope=applications.commands%20bot"),ephemeral=True)
client.start()
