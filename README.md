# Elgatron3000 Discord Bot 🤖

Elgatron3000 is an epic Discord bot designed to provide some fun and useful features to our server :)

## Features 🌟

- **Wordle but Epic**: Play wordle with your friends, only one guess each! Resets daily at 08:00, now with game stats!
- **Game Boy Emulator**: Play any Game Boy/Game Boy Colour game you would like in discord!
- **Guess The Pin**: A fun game where the bot picks a random pin, and you have to guess who wrote it!
- **Epic Games Integration**: The latest free games from the Epic Games Store are sent every day at 18:00 if something new drops!
- **Attention Grabber**: Ping someone in intervals until they go mad.
- **Management of Running Commands**: End commands early if someone gets too mad.
- **Reaction Polls**: Automatically make polls with threads to discuss stuff.
- **Built-in Gifs and videos**: A bunch of epic gifs and videos to react with.




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
Experimental features will only be available in testing mode.

    ```
    {
        "guild" : GUILD_ID_GOES_HERE,
        "game_channel_id" : CHANNEL_ID_GOES_HERE,
        "wordle_channel_id" : CHANNEL_ID_GOES_HERE,
        "testing_channel_id" : CHANNEL_ID_GOES_HERE,
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
