"""
Copyright (c) 2024 Yanman
Twitter: https://x.com/0xyanman
"""

import discord
from discord.ext import commands
from discord import app_commands
import requests
import os
import re
import sys
import time
from typing import Dict, List

# --- TOKEN ---
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
print(f"[DEBUG] Loaded TOKEN? {'✅ Yes' if TOKEN else '❌ No'}")

if not TOKEN:
    print("❌ ERROR: DISCORD_BOT_TOKEN environment variable not set!")
    exit(1)

# --- DISCORD INTENTS ---
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content
intents.guilds = True
print("[DEBUG] Discord intents enabled")

bot = commands.Bot(command_prefix='!', intents=intents)

# --- OPTIONAL CONFIG (can be set via environment variables) ---
# These are optional - bot will work without them
ALLOWED_CHANNEL_ID = int(os.getenv('ALLOWED_CHANNEL_ID', '0')) or None  # Optional: restrict !call to specific channel
MENTION_ROLE_ID = int(os.getenv('MENTION_ROLE_ID', '0')) or None  # Optional: role to mention in threads

# --- HELPER: CHECK VALID SOLANA ADDRESS ---
def is_valid_solana_address(addr: str) -> bool:
    """Check if address is a valid Solana address (32-44 base58 characters)"""
    return bool(re.fullmatch(r'[1-9A-HJ-NP-Za-km-z]{32,44}', addr))

# --- HELPER: FETCH POOL DATA FROM METEORA ---
def fetch_meteora_pools(ca: str) -> List[Dict]:
    """Fetch Meteora DLMM pools for a given contract address"""
    print(f"[DEBUG] Fetching Meteora pools for {ca} using all_by_groups API")
    base_url = 'https://dlmm-api.meteora.ag/pair/all_by_groups'
    
    target_contract = ca
    
    try:
        start_time = time.time()
        print(f"[DEBUG] Using all_by_groups API: {base_url}")
        print(f"[DEBUG] Search term: {target_contract}")
        sys.stdout.flush()
        
        params = {
            'search_term': target_contract,  # Filter by contract address
            'sort_key': 'tvl',  # Sort by TVL to get top pools
            'order_by': 'desc',  # Descending order (highest TVL first)
            'limit': 50  # Get top 50 pools (enough to sort & get top 10)
        }
        
        print(f"[DEBUG] Making request with search_term...")
        sys.stdout.flush()
        
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract pools from groups structure
        matching_pools = []
        if isinstance(data, dict) and 'groups' in data:
            for group in data.get('groups', []):
                pools = group.get('pairs', [])
                for pool in pools:
                    try:
                        mint_x = pool.get('mint_x', '').lower()
                        mint_y = pool.get('mint_y', '').lower()
                        target_lower = target_contract.lower()
                        
                        # Double check: pool must match contract address
                        if target_lower in [mint_x, mint_y]:
                            name = pool.get('name', '').strip()
                            if name:
                                clean_name = name.replace(' DLMM', '').replace('DLMM', '').strip()
                                separator = '/' if '/' in clean_name else '-'
                                parts = clean_name.split(separator)
                                if len(parts) >= 2:
                                    pair_name = f"{parts[0].strip()}-{parts[1].strip()}"
                                else:
                                    pair_name = clean_name
                            else:
                                matching_mint = mint_x if target_lower == mint_x else mint_y
                                pair_name = f"{matching_mint[:8]} Pair"

                            liq = float(pool.get('liquidity', 0))
                            liq_str = f"${liq/1000:.1f}K" if liq >= 1000 else f"${liq:.1f}"
                            bin_step = pool.get('bin_step', 0)
                            address = pool.get('address', '')

                            matching_pools.append({
                                'pair': pair_name,
                                'bin': f"{bin_step}/5",
                                'liq': liq_str,
                                'raw_liq': liq,
                                'address': address
                            })
                    except Exception as e:
                        # Skip error pools, continue
                        continue
        
        total_time = time.time() - start_time
        print(f"[DEBUG] ✅ API request completed in {total_time:.2f} seconds!")
        print(f"[DEBUG] ✅ Found {len(matching_pools)} matching pools (already filtered by API)")
        sys.stdout.flush()
        
        return matching_pools
        
    except requests.exceptions.Timeout:
        print("[ERROR] Request timeout - API did not respond within 30 seconds")
        raise Exception("Request timeout - API did not respond. Please try again later.")
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] Connection error: {e}")
        raise Exception(f"Connection error: Could not connect to API. {str(e)}")
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP error: {e}")
        raise Exception(f"HTTP error: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error in fetch_meteora_pools: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        raise

# --- EVENT: BOT ONLINE ---
@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online and ready!")
    print(f"[DEBUG] Connected to {len(bot.guilds)} guild(s): {[g.name for g in bot.guilds]}")
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"[DEBUG] Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"[ERROR] Failed to sync slash commands: {e}")

# --- AUTO DETECT: USER PASTE CONTRACT ADDRESS ---
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    print(f"[DEBUG] Message detected in #{message.channel}: {message.content[:40]}")

    content = message.content.strip()
    if is_valid_solana_address(content):
        # Handle as token pool check
        print(f"[DEBUG] Valid Solana address detected: {content}")
        try:
            await message.channel.send(f"🔍 Checking Meteora DLMM pools for token: `{content[:8]}...`")
        except Exception as e:
            print(f"[ERROR] Failed to send initial message: {e}")
            return

        try:
            print(f"[DEBUG] Starting to fetch pools for {content}")
            sys.stdout.flush()
            pools = fetch_meteora_pools(content)
            print(f"[DEBUG] Fetch completed, found {len(pools)} pools")
            sys.stdout.flush()
            
            if not pools:
                embed = discord.Embed(
                    title="Meteora DLMM Pools",
                    description=f"No pools found for token `{content[:8]}...`",
                    color=0xff0000
                )
                await message.channel.send(embed=embed)
                return

            print(f"[DEBUG] Sorting pools by liquidity...")
            pools.sort(key=lambda x: x['raw_liq'], reverse=True)
            print(f"[DEBUG] Building embed description...")
            desc = f"Found {len(pools)} pool(s) for `{content}`\n\n"

            for i, p in enumerate(pools[:10], 1):
                link = f"https://app.meteora.ag/dlmm/{p['address']}"
                desc += f"{i}. [{p['pair']}]({link}) {p['bin']} - LQ: {p['liq']}\n"

            print(f"[DEBUG] Creating embed object...")
            embed = discord.Embed(title="Meteora Pool Bot", description=desc, color=0x00ff00)
            embed.set_footer(text=f"Requested by {message.author.display_name} | © Yanman | https://x.com/0xyanman")
            print(f"[DEBUG] Sending embed with {len(pools[:10])} pools to channel {message.channel.id}")
            sys.stdout.flush()
            try:
                await message.channel.send(embed=embed)
                print(f"[DEBUG] ✅ Embed sent successfully!")
                sys.stdout.flush()
            except discord.Forbidden:
                print(f"[ERROR] Bot does not have permission to send messages in this channel")
                raise
            except discord.HTTPException as e:
                print(f"[ERROR] Discord HTTP error while sending embed: {e}")
                raise
        except requests.exceptions.Timeout:
            print("[ERROR] Request timeout")
            await message.channel.send("❌ **Timeout**: API did not respond within 30 seconds. Please try again later.")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request error: {e}")
            import traceback
            traceback.print_exc()
            await message.channel.send(f"❌ **Connection Error**: Could not connect to Meteora API. Error: {str(e)}")
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            await message.channel.send(f"❌ **Error**: {str(e)}")

    # Important: process commands like !call
    await bot.process_commands(message)

# --- COMMAND: !call <contract_address> ---
@bot.command(name="call")
async def call_token(ctx: commands.Context, ca: str):
    """Create a thread with Meteora DLMM pools for a token contract address"""
    print(f"[DEBUG] !call command triggered by {ctx.author} with ca={ca}")
    
    # Optional: Check if command is restricted to specific channel
    if ALLOWED_CHANNEL_ID and ctx.channel.id != ALLOWED_CHANNEL_ID:
        await ctx.send(f"❌ This command can only be used in <#{ALLOWED_CHANNEL_ID}>")
        return

    if not is_valid_solana_address(ca):
        await ctx.send("⚠️ Invalid Solana address!")
        return

    await ctx.send(f"🔍 Fetching Meteora DLMM pools for `{ca[:8]}...`")

    try:
        print(f"[DEBUG] Starting to fetch pools for !call command")
        pools = fetch_meteora_pools(ca)
        print(f"[DEBUG] Fetch completed, found {len(pools)} pools")
        if not pools:
            await ctx.send(f"No pools found for `{ca}`")
            return

        pools.sort(key=lambda x: x['raw_liq'], reverse=True)
        top_pool = pools[0]
        pair_name = top_pool['pair'].replace(" ", "")
        thread_name = f"{pair_name}"

        print(f"[DEBUG] Creating thread: {thread_name}")
        thread = await ctx.channel.create_thread(
            name=thread_name,
            type=discord.ChannelType.public_thread,
            reason=f"Thread created by {ctx.author}",
        )

        desc = f"Found {len(pools)} Meteora DLMM pool(s) for `{ca}`\n\n"
        for i, p in enumerate(pools[:10], 1):
            link = f"https://app.meteora.ag/dlmm/{p['address']}"
            desc += f"{i}. [{p['pair']}]({link}) {p['bin']} - LQ: {p['liq']}\n"

        embed = discord.Embed(
            title=f"Meteora DLMM Pools — {pair_name}",
            description=desc,
            color=0x00ff00
        )
        embed.set_footer(text=f"Requested by {ctx.author.display_name} | © Yanman | https://x.com/0xyanman")

        # Optional: Mention role if configured
        mention_text = f"<@&{MENTION_ROLE_ID}>" if MENTION_ROLE_ID else ""

        await thread.send(
            f"{mention_text} 💬 Thread created for `{pair_name}`\n\n"
            f"**Contract Address:** `{ca}`\n"
            f"https://solscan.io/token/{ca}"
        )

        await thread.send(embed=embed)

        thread_link = f"https://discord.com/channels/{ctx.guild.id}/{thread.id}"

        info_embed = discord.Embed(
            title=f"🧵 {pair_name}",
            description=(
                f"**Created by:** {ctx.author.mention}\n"
                f"**Channel:** {ctx.channel.mention}\n"
                f"**Token:** `{ca[:8]}...`\n"
                f"**Top Pool:** {top_pool['pair']} ({top_pool['liq']})\n\n"
                f"[🔗 Open Thread]({thread_link})"
            ),
            color=0x3498db
        )
        await ctx.send(embed=info_embed)
        print("[DEBUG] Thread and embed sent successfully")

    except requests.exceptions.Timeout:
        print("[ERROR] Request timeout in !call")
        await ctx.send("❌ **Timeout**: API did not respond within 30 seconds. Please try again later.")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request error in !call: {e}")
        import traceback
        traceback.print_exc()
        await ctx.send(f"❌ **Connection Error**: Could not connect to Meteora API. Error: {str(e)}")
    except discord.Forbidden:
        print("[ERROR] Bot does not have permission to create thread")
        await ctx.send("❌ Bot does not have permission to create thread or send messages here.")
    except Exception as e:
        print(f"[ERROR] Unexpected error in !call: {e}")
        import traceback
        traceback.print_exc()
        await ctx.send(f"❌ **Error**: {str(e)}")

# --- SLASH COMMAND: /pools ---
@bot.tree.command(name="pools", description="Get Meteora DLMM pools for a Solana token contract address")
@app_commands.describe(contract_address="The Solana token contract address to search for")
async def pools_command(interaction: discord.Interaction, contract_address: str):
    """Slash command to get Meteora pools"""
    if not is_valid_solana_address(contract_address):
        await interaction.response.send_message(
            "❌ Invalid Solana address! Please provide a valid contract address (32-44 base58 characters).",
            ephemeral=True
        )
        return
    
    await interaction.response.defer()
    
    try:
        pools = fetch_meteora_pools(contract_address)
        
        if not pools:
            embed = discord.Embed(
                title="Meteora DLMM Pools",
                description=f"No pools found for token `{contract_address[:8]}...`",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed)
            return
        
        pools.sort(key=lambda x: x['raw_liq'], reverse=True)
        desc = f"Found {len(pools)} pool(s) for `{contract_address}`\n\n"
        
        for i, p in enumerate(pools[:10], 1):
            link = f"https://app.meteora.ag/dlmm/{p['address']}"
            desc += f"{i}. [{p['pair']}]({link}) {p['bin']} - LQ: {p['liq']}\n"
        
        embed = discord.Embed(
            title="Meteora DLMM Pools",
            description=desc,
            color=0x00ff00
        )
        embed.set_footer(text=f"Requested by {interaction.user.display_name} | © Yanman | https://x.com/0xyanman")
        embed.add_field(
            name="Token Address",
            value=f"[View on Solscan](https://solscan.io/token/{contract_address})",
            inline=False
        )
        
        await interaction.followup.send(embed=embed)
        
    except requests.exceptions.Timeout:
        await interaction.followup.send("❌ **Timeout**: API did not respond within 30 seconds. Please try again later.")
    except requests.exceptions.RequestException as e:
        await interaction.followup.send(f"❌ **Connection Error**: Could not connect to Meteora API. Error: {str(e)}")
    except Exception as e:
        await interaction.followup.send(f"❌ **Error**: {str(e)}")

# --- RUN BOT ---
print("[DEBUG] Bot starting...")
try:
    bot.run(TOKEN)
except discord.errors.PrivilegedIntentsRequired as e:
    print("\n" + "="*60)
    print("❌ ERROR: Privileged Intents Not Enabled")
    print("="*60)
    print("\nThis bot requires the 'MESSAGE CONTENT INTENT' to be enabled.")
    print("\nTo fix this:")
    print("1. Go to: https://discord.com/developers/applications/")
    print("2. Select your bot application")
    print("3. Go to the 'Bot' section in the left sidebar")
    print("4. Scroll down to 'Privileged Gateway Intents'")
    print("5. Enable 'MESSAGE CONTENT INTENT'")
    print("6. Save changes")
    print("7. Restart the bot")
    print("\n" + "="*60)
    sys.exit(1)

