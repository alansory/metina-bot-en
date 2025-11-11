# Metina Pool Bot - Universal Discord Bot

A universal Discord bot that can be used on any Discord server to fetch and display Meteora DLMM pools for Solana token contract addresses.

## Features

- **Auto-detect**: Automatically detects when a Solana contract address is pasted in any channel and shows available Meteora pools
- **!call command**: Creates a thread with pool information for a token
- **/pools slash command**: Modern slash command to get pool information
- **Works on any server**: No hardcoded channel or role IDs required
- **English language**: All messages in English for universal use

## Setup

### 1. Install Dependencies

```bash
pip install discord.py requests
```

Or if you have a `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file or set environment variables:

```bash
DISCORD_BOT_TOKEN=your_bot_token_here
```

### Optional Configuration

You can optionally restrict the `!call` command to a specific channel or set a role to mention in threads:

```bash
ALLOWED_CHANNEL_ID=1234567890123456789  # Optional: restrict !call to specific channel
MENTION_ROLE_ID=9876543210987654321      # Optional: role to mention in threads
```

### 3. Run the Bot

```bash
python meteora_bot.py
```

## Usage

### Auto-detect (Paste Contract Address)

Simply paste a Solana contract address in any channel, and the bot will automatically:
- Detect the address
- Fetch Meteora DLMM pools
- Display the top 10 pools with links

### !call Command

```
!call <contract_address>
```

Creates a thread with pool information. Example:
```
!call So11111111111111111111111111111111111111112
```

### /pools Slash Command

Use the slash command `/pools` with the contract address parameter:
```
/pools contract_address:So11111111111111111111111111111111111111112
```

## Bot Permissions Required

- **Send Messages**: To send pool information
- **Create Public Threads**: For the `!call` command
- **Read Message History**: To detect pasted addresses
- **Embed Links**: To display formatted pool information

## How It Works

1. The bot listens for messages containing Solana contract addresses (32-44 base58 characters)
2. When detected, it queries the Meteora API for DLMM pools
3. Results are displayed in an embed with:
   - Pool pair names
   - Bin step information
   - Liquidity amounts
   - Direct links to Meteora pools

## API

Uses the Meteora DLMM API:
- Endpoint: `https://dlmm-api.meteora.ag/pair/all_by_groups`
- Searches by contract address
- Returns pools sorted by TVL (Total Value Locked)

## Notes

- The bot works on any Discord server without configuration
- All messages are in English
- No server-specific features (verification, welcome messages, etc.)
- Focused solely on Meteora pool information

## Troubleshooting

- **Bot not responding**: Check that the bot has proper permissions in the channel
- **API timeout**: The Meteora API may be slow; wait and try again
- **No pools found**: The token may not have any Meteora DLMM pools

