-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- clean and recreate the tournament database
drop if exists tournament;
create database tournament;

-- connect to the new tournament database
\c tournament;


-- a simple player table
create table players (
    id serial primary key,
    name varchar(255) not null
);

-- a player wins by default if he has no opponent, so loser can be null
create table matches (
    id serial primary key,
    winner int references players(id) not null,
    loser int references players(id)
);

-- aggregate the number of matches each player has joined
create view rounds as
    select players.id, count(matches) as total from players
    left join matches on matches.winner = players.id or matches.loser = players.id
    group by players.id;

-- aggregate the number of wins each player has enjoyed
create view wins as
    select players.id, count(matches.winner) as total from players
    left join matches on matches.winner = players.id
    group by players.id;
