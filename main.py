import os
import lightbulb
import datetime

from hikari import ResponseType
from hikari.messages import MessageFlag
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = lightbulb.BotApp(token = TOKEN)

@bot.command
@lightbulb.option("starting_date", "Date to backup from (YYYYMMDD)", type = str, required = True)
@lightbulb.command("backup_thread", "Backs up the chat history in this thread/channel", ephemeral = False, auto_defer = False)
@lightbulb.implements(lightbulb.SlashCommand)
async def backup_thread(ctx):
	target_date = generate_datetime_object(ctx.options.starting_date)
	thread_history = await get_message_history(ctx, target_date)

	await ctx.respond(ResponseType.DEFERRED_MESSAGE_CREATE, flags=MessageFlag.EPHEMERAL)
	await run_backup(ctx, thread_history)

	await ctx.respond("Backup complete.", flags = MessageFlag.EPHEMERAL)

@bot.command
@lightbulb.option("starting_date", "Date to cleanup from (YYYYMMDD)", type = str, required = True)
@lightbulb.command("cleanup_thread", "Clears the chat history in this thread/channel", ephemeral = False, auto_defer = False)
@lightbulb.implements(lightbulb.SlashCommand)
async def cleanup_thread(ctx):
	target_date = generate_datetime_object(ctx.options.starting_date)
	thread_history = await get_message_history(ctx, target_date)

	await ctx.respond(ResponseType.DEFERRED_MESSAGE_CREATE, flags=MessageFlag.EPHEMERAL)
	for message in thread_history:
		await bot.rest.delete_message(ctx.channel_id, message)

	await ctx.respond("Cleanup complete.", flags = MessageFlag.EPHEMERAL)

async def run_backup(ctx, target_list):
	channel_object = await ctx.bot.rest.fetch_channel(ctx.channel_id)

	with open(rf'{channel_object.name}_backup.txt', 'w') as fp:
		for message in target_list:
			if not message.content == None:
				fp.write("%s\n\n" % message.content)

def generate_datetime_object(date_str):
	target_date = datetime.datetime.strptime(date_str, "%Y%m%d")

	return target_date

async def get_message_history(ctx, target_date):
	thread_history = await ctx.bot.rest.fetch_messages(ctx.channel_id, after = target_date)

	return thread_history

bot.run()