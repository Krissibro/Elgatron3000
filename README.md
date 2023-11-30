# Elgatron3000 Discord Bot 🤖

Elgatron3000 is a very cool and epic Discord bot designed to provide a mix of reminders, peer pressure and some fun features for our server.

## Features 🌟

- **Attention Grabber**: Ping someone at intervals until they go mad.
- **Management of Running Commands**: End commands early if someone are too annoyed.
- **Epic Games Integration**: Get information about the currently free games on Epic Games Store.
- **Wordle but Epic**: Play wordle with your friends, only one guess each. Resets daily.

## Installation 🛠️

1. **Clone the Repository**
```bash
git clone https://github.com/Krissibro/Elgatron3000.git
cd Elgatron3000
```

2. **Set Up Environment Variables**: 
Create a `token.env` file in the root directory and add your Discord bot token:
```
TOKEN=YOUR_DISCORD_TOKEN_HERE
```

3. **Set Up Config**: 
Create a `config.json` file in the `utilities` directory. \
Add your guild ID (server ID) and whether this instance of the bot is for testing or production.

```
{
    "guild" : ID_GOES_HERE,
    "testing" : BOOL_GOES_HERE
}
```

4. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

5. **Run the Bot**:
```bash
python3 bot.py
```
