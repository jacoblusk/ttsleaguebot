import discord
import json
import aiohttp
import traceback
import time
import urllib

from discord import app_commands

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1yk-mlnwK9jMQW8feQH-CtoBEMqURmuCwnEIw_pVHtEU"
RANGE_NAME = "A1:L"
SCRYFALL_SEARCH_URL = "https://api.scryfall.com/cards/search"


creds = service_account.Credentials.from_service_account_file(
    "credentials.json", scopes=SCOPES
)
service = build("sheets", "v4", credentials=creds)

async def scryfall_commander_lookup(cardname: str):
    params = {
        'q': f"{cardname} is:commander",
        'order': 'edhrec'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(SCRYFALL_SEARCH_URL, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if data['object'] == 'list' and data['total_cards'] > 0:
                    return data['data'][0]["name"]
                else:
                    return "No cards found."
            else:
                return f"Error: {response.status}"

    print(results)

def get_next_increment_value():
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME)
        .execute()
    )
    values = result.get("values", [])
    return len(values) + 1


class TTSLeagueClient(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        await self.tree.sync()
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")


class ReportLeagueResult(discord.ui.Modal, title="Report League Result"):
    async def on_submit(self, interaction: discord.Interaction):
        commanders = [child.value for child in self._children]

        full_commander_names = []
        for commander in commanders:
            if "," in commander:
                parnters = [await scryfall_commander_lookup(partner.strip()) for partner in commander.split(",")]
                full_commander_names.append("/".join(parnters))
            else:
                full_commander_names.append(await scryfall_commander_lookup(commander))

        
        body = {
            "values": [
                [
                    get_next_increment_value(),
                    self.players[0].id,
                    self.players[1].id,
                    self.players[2].id,
                    self.players[3].id,
                    *full_commander_names,
                    self.winner.id,
                    int(time.time()),
                    "Empty",
                ]
            ]
        }

        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=SPREADSHEET_ID,
                range=RANGE_NAME,
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body=body,
            )
            .execute()
        )

        await interaction.response.send_message(
            f"League report successful!", ephemeral=True
        )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        await interaction.response.send_message(
            "Oops! Something went wrong.", ephemeral=True
        )

        traceback.print_exception(type(error), error, error.__traceback__)


client = TTSLeagueClient()


@client.tree.command(description="Report league results.")
async def report(
    interaction: discord.Interaction,
    winner: discord.Member,
    player1: discord.Member,
    player2: discord.Member,
    player3: discord.Member,
    player4: discord.Member,
):
    modal = ReportLeagueResult()
    modal.players = [player1, player2, player3, player4]
    modal.winner = winner

    for player in modal.players:
        modal.add_item(
            discord.ui.TextInput(
                label=f"{player.nick}'s Commander(s)",
                placeholder=f"Type {player.nick}'s commander(s) here...",
            )
        )

    await interaction.response.send_modal(modal)


with open("bot_token", "r") as fin:
    bot_token = fin.read()
client.run(bot_token)
