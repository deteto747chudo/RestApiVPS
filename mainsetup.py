# -*- coding: utf-8 -*-

import logging
import json
import os
from colorama import Fore
from TwitchChannelPointsMiner import TwitchChannelPointsMiner
from TwitchChannelPointsMiner.logger import LoggerSettings, ColorPalette
from TwitchChannelPointsMiner.classes.Chat import ChatPresence
from TwitchChannelPointsMiner.classes.Discord import Discord
from TwitchChannelPointsMiner.classes.Telegram import Telegram
from TwitchChannelPointsMiner.classes.Matrix import Matrix
from TwitchChannelPointsMiner.classes.Pushover import Pushover
from TwitchChannelPointsMiner.classes.Settings import Priority, Events, FollowersOrder
from TwitchChannelPointsMiner.classes.entities.Bet import Strategy, BetSettings, Condition, OutcomeKeys, FilterCondition, DelayMode
from TwitchChannelPointsMiner.classes.entities.Streamer import Streamer, StreamerSettings
from keep_alive import keep_alive

keep_alive()

# Path to the JSON file that will be updated by the REST API
STREAMERS_FILE = 'streamers.json'

def load_streamers_from_file():
    if os.path.exists(STREAMERS_FILE):
        with open(STREAMERS_FILE, 'r') as file:
            data = json.load(file)
            return data.get('streamers', [])
    return []

# Load streamer names from JSON file
streamers_list = load_streamers_from_file()

# Create Streamer instances from the list of names
streamers = [
    Streamer(
        name,
        settings=StreamerSettings(
            make_predictions=False,
            follow_raid=True,
            claim_drops=True,
            watch_streak=True,
            bet=BetSettings(
                strategy=Strategy.SMART,
                percentage=5,
                stealth_mode=True,
                percentage_gap=20,
                max_points=234,
                filter_condition=FilterCondition(
                    by=OutcomeKeys.TOTAL_USERS,
                    where=Condition.LTE,
                    value=800
                )
            )
        )
    ) for name in streamers_list
]

twitch_miner = TwitchChannelPointsMiner(
    username="rainboxsixgays",
    password="Deniskoto0711",  # If no password will be provided, the script will ask interactively
    claim_drops_startup=False,  # If you want to auto claim all drops from Twitch inventory on the startup
    priority=[  # Custom priority in this case for example:
        Priority.STREAK,  # - We want first of all to catch all watch streak from all streamers
        Priority.DROPS,  # - When we don't have anymore watch streak to catch, wait until all drops are collected over the streamers
        Priority.ORDER  # - When we have all of the drops claimed and no watch-streak available, use the order priority (POINTS_ASCENDING, POINTS_DESCENDING)
    ],
    enable_analytics=False,  # Disables Analytics if False. Disabling it significantly reduces memory consumption
    disable_ssl_cert_verification=False,  # Set to True at your own risk and only to fix SSL: CERTIFICATE_VERIFY_FAILED error
    disable_at_in_nickname=False,  # Set to True if you want to check for your nickname mentions in the chat even without @ sign
    logger_settings=LoggerSettings(
        save=True,  # If you want to save logs in a file (suggested)
        console_level=logging.INFO,  # Level of logs - use logging.DEBUG for more info
        console_username=False,  # Adds a username to every console log line if True. Also adds it to Telegram, Discord, etc. Useful when you have several accounts
        auto_clear=True,  # Create a file rotation handler with interval = 1D and backupCount = 7 if True (default)
        time_zone="",  # Set a specific time zone for console and file loggers. Use tz database names. Example: "America/Denver"
        file_level=logging.DEBUG,  # Level of logs - If you think the log file it's too big, use logging.INFO
        emoji=True,  # On Windows, we have a problem printing emoji. Set to false if you have a problem
        less=False,  # If you think that the logs are too verbose, set this to True
        colored=True,  # If you want to print colored text
        color_palette=ColorPalette(  # You can also create a custom palette color (for the common message).
            STREAMER_online="GREEN",  # Don't worry about lower/upper case. The script will parse all the values.
            streamer_offline="red",  # Read more in README.md
            BET_wiN=Fore.MAGENTA  # Color allowed are: [BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET].
        ),
        telegram=Telegram(  # You can omit or set to None if you don't want to receive updates on Telegram
            chat_id=123456789,  # Chat ID to send messages @getmyid_bot
            token="123456789:shfuihreuifheuifhiu34578347",  # Telegram API token @BotFather
            events=[Events.STREAMER_ONLINE, Events.STREAMER_OFFLINE,
                    Events.BET_LOSE, Events.CHAT_MENTION],  # Only these events will be sent to the chat
            disable_notification=True,  # Revoke the notification (sound/vibration)
        ),
        discord=Discord(
            webhook_api="https://discord.com/api/webhooks/1281029614759841874/zA8Vcuw8LxuQPmy93eiArnMXluelpMIdrSJ_1AxU93fM0Behy6eGRT53-oAxmPVjRTp-",  # Discord Webhook URL
            events=[Events.STREAMER_ONLINE, Events.STREAMER_OFFLINE,
                    Events.BET_LOSE, Events.CHAT_MENTION],  # Only these events will be sent to the chat
        ),
        matrix=Matrix(
            username="twitch_miner",  # Matrix username (without homeserver)
            password="...",  # Matrix password
            homeserver="matrix.org",  # Matrix homeserver
            room_id="...",  # Room ID
            events=[Events.STREAMER_ONLINE, Events.STREAMER_OFFLINE, Events.BET_LOSE],  # Only these events will be sent to the chat
        ),
        pushover=Pushover(
            userkey="YOUR-ACCOUNT-TOKEN",  # Login to https://pushover.net/, the user token is on the main page.
            token="YOUR-APPLICATION-TOKEN",  # Create an application on the website, and use the token shown in your application.
            priority=0,  # Read more about priority here: https://pushover.net/api#priority
            sound="pushover",  # A list of sounds can be found here: https://pushover.net/api#sounds
            events=[Events.CHAT_MENTION, Events.DROP_CLAIM],  # Only these events will be sent.
        )
    ),
    streamer_settings=StreamerSettings(
        make_predictions=True,  # If you want to Bet / Make prediction
        follow_raid=True,  # Follow raid to obtain more points
        claim_drops=True,  # We can't filter rewards based on stream. Set to False for skipping viewing counter increase and you will never obtain a drop reward from this script.
        claim_moments=True,  # If set to True, https://help.twitch.tv/s/article/moments will be claimed when available
        watch_streak=True,  # If a streamer goes online change the priority of streamers array and catch the watch streak.
        chat=ChatPresence.ONLINE,  # Join IRC chat to increase watch-time [ALWAYS, NEVER, ONLINE, OFFLINE]
        bet=BetSettings(
            strategy=Strategy.SMART,  # Choose your strategy!
            percentage=5,  # Place the x% of your channel points
            percentage_gap=20,  # Gap difference between outcomesA and outcomesB (for SMART strategy)
            max_points=50000,  # If the x percentage of your channel points is greater than bet_max_points set this value
            stealth_mode=True,  # If the calculated amount of channel points is greater than the highest bet, place the highest value minus 1-2 points
            delay_mode=DelayMode.FROM_END,  # When placing a bet, we will wait until `delay` seconds before the end of the timer
            delay=6,
            minimum_points=20000,  # Place the bet only if we have at least 20k points.
            filter_condition=FilterCondition(
                by=OutcomeKeys.TOTAL_USERS,  # Where apply the filter. Allowed [PERCENTAGE_USERS, ODDS_PERCENTAGE, ODDS, TOP_POINTS, TOTAL_USERS, TOTAL_POINTS]
                where=Condition.LTE,  # 'by' must be [GT, LT, GTE, LTE] than value
                value=800
            )
        )
    )
)

# Mine the streamers
twitch_miner.mine(
    streamers,  # Use the list of Streamer instances
    followers=False,
    followers_order=FollowersOrder.ASC
)
