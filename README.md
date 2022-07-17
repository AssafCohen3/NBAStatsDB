Collect and manage an NBA stats Database with many resources.
<br/>
the data can be queried for some crazy NBA stats we all love.

# Examples 
* Players stats at elimination games 
* Players stats when underdog/favorite in a playoff serie
* most assists from the bench in a playoff serie under 22 years old
* players stats at triple double games
* most games in a row 
* shot finder with play by play data(beta)
* Decade with most trades of all stars or hof to teams who made the finals the year before
* Players to break franchise points record with a clutch shot(hye giannis)
* Average games missed by an average player in a decade
* etc...

# Resources #
| Resource Name       | Description                                                                                            | Tables               | Source            | Estimated time to fully download                                                                             |
|---------------------|--------------------------------------------------------------------------------------------------------|----------------------|-------------------|--------------------------------------------------------------------------------------------------------------|
| Boxscores           | the most basic resource. <br/>row for every game of a player or a team.                                | BoxScoreP, BoxScoreT | stats.nba         | 5~ minutes                                                                                                   |
| Players             | an index of all the players with bio data.                                                             | Player               | stats.nba         | immediate                                                                                                    |
| Playoff Series      | Playoff serie with details about the winners, level, title                                             | PlayoffSerieSummary  | BREF              | 10~ minutes                                                                                                  |
| PBP                 | all events of every game since 1996-97                                                                 | Event                | stats.nba         | 12~ hours                                                                                                    |
| Awards              | all awards of all players.                                                                             | Awards               | stats.nba         | 90~ minutes                                                                                                  |
| HOF/Retired jersies | HOF entrances and retired jersies                                                                      | Awards               | stats.nba         | 5~ minutes                                                                                                   |
| Birthdates          | complete the missing birthdates in the Players resource                                                | Player               | stats.nba         | 90~ minutes                                                                                                  |
| BREF Mapping        | mapping from BREF Player ID to NBA Player ID. very important if we want to use players stats from BREF | PlayerMapping        | CSV file, BREF    | varying. if the initial file is updated to at least the last season this should not take more than 5 minutes |
| BREF Players        | an index of all the players with bio data from BREF.                                                   | BREFPlayer           | BREF              | 10~ minutes                                                                                                  |
| Starters            | Starters and bench data on games since 1983                                                            | BoxScoreP            | BREF              | 30~ minutes                                                                                                  |
| Transactions        | Every transaction in the history of the league                                                         | Transactions         | BREF              | 5~ minutes                                                                                                   |
| Odds                | Odds data of the favorites in the playoffs since 1973                                                  | Odds                 | sportsoddshistory | 5~ minutes                                                                                                   |

## More detailes ## 
### Play by play ###
* using the great pbpstats library of dblackrun.
* there is arround 27000 games to be collected so it will take a lot of time(12 hours for me)
* this will inflate the storage space of the database to around 4 gigabytes

### Awards ###
* the hof and retired jerseys is quick since it can be retrieved through the teams endpoint so only 50 requests is required
* other awards require a request per player which means arround 5000 requests(this will take some hours)

### Transactions ###
* i written a parser to scrape transactions from BREF
* the parser is sensitive to changes in the transactions page syntax so the output 
may be incorrect or crush(important to update the parser with new transactions)
* this require only a request per season so downloading and parsing all transactions should take arround 2 minutes

# Setting up
* requires Python >=3.6  
<!-- end of the list -->

download the project and install required libraries
```bash
git clone https://github.com/AssafCohen3/nba_utils.git
cd nba_utils
pip3 install -r requirements.txt
```

# How to use #

## First use ##
create and update the database with the base resources:
```bash
python3 boxscores_db.py #update only the base resoureces(boxscore tables, players index, bref players index, playoff series)
```

## Download resource ##
run the main script with arguments specifying which resources to download in addition to the base resources
<br />
for example:
```bash
python3 boxscores_db.py -e all #update the base resources and all missing events
```

### options ###
| option               | Description                                         | Default value | Valid values                                                                      |
|----------------------|-----------------------------------------------------|---------------|-----------------------------------------------------------------------------------|
| -d                   | debug mode. log http requests                       |               |                                                                                   |
| -e \[SEASON_TYPE\]   | update missing events of the given season type.     | all           | all, playoff, regular, playin, allstar                                            |
| -o                   | update missing odds data.                           |               |                                                                                   |
| -aw \[TYPE/PLAYER\]  | Download players awards data                        | all           | all, active, Integer - Player ID(for example 2430)                                |
| -hof                 | Download all teams HOF players and retired jersies  |               |                                                                                   |
| -b                   | update missing birthdates data.                     |               |                                                                                   |
| -starters            | update missing starters data                        |               |                                                                                   |
| -t                   | download transactions data                          | all           | all, Integer - season to download transactions of it(for example 2004)            |
| -wv \[path to file\] | Export views to a file                              | none          | valid path to a file to write the views into(for example Database/views.txt)      |
| -lv \[path to file\] | Load views from file(Only load trusted files!!!!!)  | none          | valid path to a file to load views from(for example Database/views.txt)           |
| -em \[path to file\] | Export the BREF mappings to a file                  | none          | valid path to a file to save the mappings in(for example players_ids/players.csv) |
| -browse              | Open a lightweight sqlite browser for simple usages |               |                                                                                   |

## Update the database ##
to update a resource just download it as in first use. 
<br />
the library will download only the necessary updates
(except for the awards and HOF resources which will start from scratch in any update)

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