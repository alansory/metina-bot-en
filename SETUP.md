# 🚀 Quick Setup Guide - Meteora Pool Bot

Quick guide for setting up and deploying the bot to Railway.

## 📦 Required Files

Make sure your project has these files:

```
DiscordBot/
├── meteora_bot.py      # Main bot file
├── Procfile            # Railway start command
├── requirements.txt    # Python dependencies
├── runtime.txt         # Python version (optional)
└── .gitignore          # Git ignore file
```

---

## ⚡ Quick Start

### 1. Setup Discord Bot

1. Open [Discord Developer Portal](https://discord.com/developers/applications)
2. **New Application** → Give it a name → **Create**
3. Click **Bot** → **Add Bot** → **Yes, do it!**
4. **Copy Token** (save it for later!)
5. Enable **MESSAGE CONTENT INTENT** (REQUIRED!)
6. **OAuth2** → **URL Generator**:
   - Scopes: `bot`, `applications.commands`
   - Permissions: Send Messages, Embed Links, Read History, Create Threads
7. Copy URL and invite bot to server

### 2. Deploy to Railway

#### Option A: Deploy from GitHub (Recommended)

1. Push code to GitHub
2. Open [railway.app](https://railway.app)
3. **New Project** → **Deploy from GitHub repo**
4. Select your repository
5. Railway auto-detects Python

#### Option B: Manual Deploy

1. Open [railway.app](https://railway.app)
2. **New Project** → **Empty Project**
3. **New** → **GitHub Repo** (or upload files)
4. Select repository

### 3. Set Environment Variables

In Railway dashboard:

1. Click **Variables** tab
2. Add:
   ```
   DISCORD_BOT_TOKEN=your_bot_token_here
   ```
3. **Add** → **Deploy**

### 4. Check Logs

1. Click **Deployments**
2. Click latest deployment
3. **View Logs** → Check if bot is online

---

## ✅ Checklist

- [ ] Bot created in Discord Developer Portal
- [ ] Token copied and saved
- [ ] MESSAGE CONTENT INTENT enabled
- [ ] Bot invited to server with permissions
- [ ] Code pushed to GitHub
- [ ] Project created in Railway
- [ ] DISCORD_BOT_TOKEN set in Railway Variables
- [ ] Deploy successful
- [ ] Bot online in Discord

---

## 🧪 Test Bot

1. Paste Solana contract address in channel
2. Bot should auto-respond with pools
3. Test: `!call <contract_address>`
4. Test: `/pools <contract_address>`

---

## 📝 File Contents

### `Procfile`
```
worker: python meteora_bot.py
```

### `requirements.txt`
```
discord.py==2.3.2
requests==2.31.0
```

### `runtime.txt` (Optional)
```
python-3.11.0
```

---

## 🆘 Troubleshooting

**Bot not online:**
- Check `DISCORD_BOT_TOKEN` is correct
- Check logs in Railway for errors
- Make sure intents are enabled

**Bot not responding:**
- Check bot is invited to server
- Check bot has permission in channel
- Check logs for errors

**Build failed:**
- Check `requirements.txt` is correct
- Check `Procfile` format is correct
- Check Python version in `runtime.txt`

---

## 📚 Full Documentation

See `RAILWAY_DEPLOY.md` for complete guide.

---

## 🎉 Done!

Your bot is now online and ready to use on any Discord server!

