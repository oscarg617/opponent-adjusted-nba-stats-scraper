# Opponent Adjusted NBA Scraper

This is a package that collects data from [stats.nba.com](https://www.stats.nba.com) and provides methods focused on adjusting a player's statistics by their opponents defensive strength.

## Installing
### Via `pip`
Install using the following command:

```
pip install opponent_adjusted_nba_scraper
```

### Via GitHub
Or, you can clone this repo to a Git repository on your local machine.

## About

This is my first time writing a PyPi package, and I'm glad I decided to do this because it makes the process of adjusting player's stats that I've worked on for years a lot easier and faster. The stats required for this scraper only go back to the 1996-97 season, which would not have been the case if I had used [basketball-reference](https://www.basketball-reference.com). However, I couldn't find a way to access playoff stats on bball-ref, so I'm hoping to find a way to access these stats and update this scraper to allow for searches before the '97 season.

## API

You can find the full details for this API [here](API.md).

## Credits

I borrowed the implementation for `lookup.py` and the names of all NBA players up to the 2020-21 season in `names.txt` from [Vishaal Agartha](https://github.com/vishaalagartha/basketball_reference_scraper).
