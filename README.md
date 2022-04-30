A collection of my scripts to download and analyze nba boxscores, awards, and play by play data.

# Examples
* Players stats at elimination games
* Players stats when underdog/favorite in a playoff serie
* most assists from the bench in a playoff serie under 22 years old
* players stats at triple double games
* most games in a row 
* shot finder with play by play data(beta)
* etc...

# Play by play
* i added support in the pbpstats library and play by play can now be downloaded.
* there is arround 27000 games to be collected so it will take a lot of time(12 hours for me)
* the cache can grow up to gigabytes so consider running without caching
* the database will also take a lot of space

# Awards
* i added awards downloader but yet to fully tested it.
* it looks like the data in this endpoint is inconsistent so consider give up on this one.
* the hof and retired jerseys is quick since it can be retrieved through the teams endpoint so only 50 requests is required
* other awards require a request per player which means arround 5000 requests(this will take some hours)
* like the play by play, the cache can grow up to gigabytes so consider running without caching

# Setting up
* requires Python >=3.6  
<!-- end of the list -->

download the project and install required libraries
```bash
git clone https://github.com/AssafCohen3/nba_utils.git
cd nba_utils
pip3 install -r requirements.txt
```

create and update the database with one of the options below(or combine them):
```bash
python3 boxscores_db.py #update only the boxscore tables without caching
python3 boxscores_db.py -c #update only the boxscore tables with caching(downloaded files will be saved)
python3 boxscores_db.py -m #update only the boxscore tables with misses caching(files the script failed to download will be mark as missing and be ignored next time)
python3 boxscores_db.py -o #updates the boxscore tables and the odds table
python3 boxscores_db.py -e all #updates the boxscore tables and the play by play data of all games
python3 boxscores_db.py -b #updates the boxscore tables and the players birthdate(may take some time)
python3 boxscores_db.py -hof #updates the boxscore tables and the hall of fame inductees(not complete without awards option but almost complete)
python3 boxscores_db.py -aw #updates the boxscore tables and the awards table(will take some time)
python3 boxscores_db.py -starters #updates the boxscore tables and updating starters data(require a request per team per season so will take some time)
```

after that step you can start query all the boxscores that had been collected. <br/>
the database path is Database/boxscores_full_database.sqlite

# Downloading options
* -c, Cache downloaded files
* -m, Cache and ignore missing files
* -o, Update Odds table
* -e (all|regular|allstar|playoff), default: all, download play by play data
* -b, downloads birthdates
* -hof, downloads hof and retired jersies data
* -aw, downloads awards data
* -starters, downloads starters data

# Views
you can find the views i created in Database/views.txt.
to load them execute:
```bash
python3 boxscores_db.py -lv Database/views.txt
```
you can also save views you have created with
```bash
python3 boxscores_db.py -wv Database/views.txt #or any other output file
```

# Queries
i saved some of the queries which wasnt saved as views in Database/Queries/

# Misc
this is just a collection of scripts that visualize and collect data <br/>
<b>TODO: add explanation to each script</b>