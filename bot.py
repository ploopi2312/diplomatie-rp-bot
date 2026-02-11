import discord
from discord.ext import commands
import json
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "factions.json"
PANEL_FILE = "panel_message.json"

RELATIONS = {
    "alliance":  ("🤝 Alliance", 0x006400),
    "bonne":     ("🟩 Bonne entente", 0x66ff66),
    "neutre":    ("⚖️ Neutre", 0xffff00),
    "frictions": ("⚠️ Début de frictions", 0xffc266),
    "mauvaise":  ("😠 Mauvaise entente", 0xff8c00),
    "guerre":    ("⚔️ Guerre", 0xff0000)
}

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def build_embed(data):
    embed = discord.Embed(
        title="📜 État diplomatique des factions",
        description="Relations actuelles entre les groupes du serveur",
        color=0x2f3136
    )

    for key, (label, _) in RELATIONS.items():
        groups = [name for name, rel in data.items() if rel == key]
        if groups:
            embed.add_field(
                name=label,
                value="\n".join(f"• {g}" for g in groups),
                inline=False
            )

    return embed

async def refresh_panel(interaction):
    data = load_data()
    embed = build_embed(data)

    if os.path.exists(PANEL_FILE):
        with open(PANEL_FILE, "r") as f:
            panel = json.load(f)
        channel = bot.get_channel(panel["channel_id"])
        message = await channel.fetch_message(panel["message_id"])
        await message.edit(embed=embed)
    else:
        msg = await interaction.channel.send(embed=embed)
        with open(PANEL_FILE, "w") as f:
            json.dump(
                {"channel_id": msg.channel.id, "message_id": msg.id},
                f
            )

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")

@bot.tree.command(name="add")
async def add(interaction: discord.Interaction, nom: str, entente: str):
    data = load_data()
    if entente not in RELATIONS:
        await interaction.response.send_message("❌ Entente invalide.", ephemeral=True)
        return
    data[nom] = entente
    save_data(data)
    await refresh_panel(interaction)
    await interaction.response.send_message(f"✅ Groupe **{nom}** ajouté.", ephemeral=True)

@bot.tree.command(name="mod")
async def mod(interaction: discord.Interaction, nom: str, entente: str):
    data = load_data()
    if nom not in data:
        await interaction.response.send_message("❌ Groupe introuvable.", ephemeral=True)
        return
    data[nom] = entente
    save_data(data)
    await refresh_panel(interaction)
    await interaction.response.send_message(f"✏️ Entente de **{nom}** modifiée.", ephemeral=True)

@bot.tree.command(name="del")
async def delete(interaction: discord.Interaction, nom: str):
    data = load_data()
    if nom not in data:
        await interaction.response.send_message("❌ Groupe introuvable.", ephemeral=True)
        return
    del data[nom]
    save_data(data)
    await refresh_panel(interaction)
    await interaction.response.send_message(f"🗑️ Groupe **{nom}** supprimé.", ephemeral=True)

@bot.tree.command(name="show")
async def show(interaction: discord.Interaction):
    await refresh_panel(interaction)
    await interaction.response.send_message("📜 Panneau diplomatique mis à jour.", ephemeral=True)

import os
bot.run(os.getenv("DISCORD_TOKEN"))

