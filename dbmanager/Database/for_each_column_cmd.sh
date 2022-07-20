#!/bin/bash

# sumable columns
sqlite3 /home/assaf/PycharmProjects/OldProjects/nba_utils/Database/boxscores_full_database.sqlite \
    'SELECT name FROM PRAGMA_TABLE_INFO("BoxScoreP") where name not like "%PCT%";' 2>/dev/null | \
    while read c ; do
        # do something for sumable columns
        echo "sum($c) as TOTAL_$c, round(avg($c), 2) as AVG_$c,";
    done;
# non sumable columns
sqlite3 /home/assaf/PycharmProjects/OldProjects/nba_utils/Database/boxscores_full_database.sqlite \
    'SELECT distinct substr(name, 1, instr(name, "_") - 1) FROM PRAGMA_TABLE_INFO("BoxScoreP") where name like "%PCT%";' 2>/dev/null | \
    while read c ; do
        # do something for non sumable columns
        echo "round(avg(${c}M)/avg(${c}A), 2) as ${c}_PCT,";
    done;