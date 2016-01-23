#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    database = connect()

    database.cursor().execute("delete from matches;")

    database.commit()
    database.close()


def deletePlayers():
    """Remove all the player records from the database."""
    database = connect()

    database.cursor().execute("delete from players;")

    database.commit()
    database.close()


def countPlayers():
    """Returns the number of players currently registered."""
    database = connect()

    cursor = database.cursor()
    cursor.execute("select count(*) from players;")

    # our table will have one row, so pull just that row
    row = cursor.fetchone()

    database.close()

    # cast the count to an int and return
    return int(row[0])


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    database = connect()

    database.cursor().execute("insert into players values (default, %s);", (name,))

    database.commit()
    database.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    database = connect()

    query = '''
        select players.id, players.name, wins.total as wins, rounds.total as matches from players
        left join wins on wins.id = players.id
        left join rounds on rounds.id = players.id
        order by wins desc;
    '''

    cursor = database.cursor()
    cursor.execute(query)

    rows = cursor.fetchall()

    database.close()

    # the win and match counts are returned as longs
    # we cast them back to int to keep things clean
    clean_rows = list()

    for row in rows:
        clean_rows.append((int(row[0]), row[1], int(row[2]), int(row[3])))

    return clean_rows


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    database = connect()

    query = "insert into matches values (default, %s, %s);"
    cursor = database.cursor().execute(query, (winner, loser))

    database.commit()
    database.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings()

    # split into groups of two with a potential single remainder
    pairs = [standings[i:i+2] for i in xrange(0, len(standings), 2)]

    swiss_pairings = list()

    for pair in pairs:
        # save the first player's information
        one_id = pair[0][0]
        one_name = pair[0][1]

        # if there is a second player, store her information, or set to None if no player exists
        if len(pair) == 2:
            two_id = pair[1][0]
            two_name = pair[1][1]
        else:
            two_id = two_name = None

        # append the final pairing to the list of swiss pairings
        swiss_pairings.append((one_id, one_name, two_id, two_name))

    return swiss_pairings
