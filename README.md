# Defense Adjusted NBA Stats

This is a package that collects data from [basketball-reference.com](https://www.basketball-reference.com) and [stats.nba.com](https://www.stats.nba.com) and provides endpoints that adjust a player's statistics depending on their opponents defensive strength.

## Why adjust stats?

Numbers at face-value don't always tell the full story. For example, if player A scores 30 points on 50% from the field, and player B scores 27 points on 47% from the field, we could come to the conclusion that player A had a better scoring game.

However, what if player B faced one of the best defensive teams in the league, and player A faced a mediocre defensive team? How does that change how we view those performances?

This package attempts to provide a more even playing field with statistics by using the opponent team's defensive to adjust a player scoring and efficiency. For more details about how stats are "adjusted", see the methodology [here](https://github.com/oscarg617/dans/blob/main/METHODOLOGY.md).

Stats from basketball-reference for this package go back to the 1970-71 season, and stats from nba-stats only go back to the 1996-97 season.

You can find the full details for this API [here](https://github.com/oscarg617/dans/blob/main/API.md).

## Installing
### Via `pip`
Install using the following command:

```
pip install dans
```

### Via GitHub
Or, you can clone this repo to a Git repository on your local machine.


## License & Terms of Use

## API  Package

The `dans` package is Open Source with an [MIT License](https://github.com/oscarg617/dans/blob/main/LICENSE).

## NBA.com

NBA.com has a [Terms of Use](https://www.nba.com/termsofuse) regarding the use of the NBA’s digital platforms.
