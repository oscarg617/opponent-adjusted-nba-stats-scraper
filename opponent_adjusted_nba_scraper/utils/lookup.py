'''Credit to https://github.com/vishaalagartha for the following algorithm
used to lookup players on basketball reference.'''
import os
import unidecode

# Bounded levenshtein algorithm credited to user amirouche on stackoverflow.
# Implementation borrowed from
# https://stackoverflow.com/questions/59686989/levenshtein-distance-with-bound-limit
def _levenshtein(string1, string2, maximum):
    if len(string1) > len(string2):
        string1, string2 = string2, string1

    distances = range(len(string1) + 1)
    for index2, char2 in enumerate(string2):
        distances_ = [index2+1]
        for index1, char1 in enumerate(string1):
            if char1 == char2:
                distances_.append(distances[index1])
            else:
                distances_.append(1 + min((distances[index1],
                                           distances[index1 + 1],
                                           distances_[-1])))
        if all((x >= maximum for x in distances_)):
            return -1
        distances = distances_
    return distances[-1]


# User input is normalized/anglicized, then assigned a levenshtein score to
# find the closest matches. If an identical and unique match is found, it is
# returned. If many matches are found, either identical or distanced, all
# are returned for final user approval.
# Implementation borrowed from https://github.com/vishaalagartha/basketball_reference_scraper
def _lookup(player, ask_matches = True):
    path = os.path.join(os.path.dirname(__file__), 'names.txt')
    normalized = unidecode.unidecode(player)
    matches = []
    with open(path, encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            # A bound of 5 units of levenshtein distance is selected to
            # account for possible misspellings or lingering non-unidecoded
            # characters.
            dist = _levenshtein(normalized.lower(), line[:-1].lower(), 5)
            if dist >= 0:
                matches += [(line[:-1], dist)]

    # If one match is found, return that one;
    # otherwise, return list of likely candidates and allow
    # the user to confirm specifiy their selection.

    if len(matches) == 1 or ask_matches is False:
        matches.sort(key=lambda tup: tup[1])
        if ask_matches:
            print(f"You searched for \"{player}\"\n{len(matches)} result found.\n{matches[0][0]}")
            print(f"Results for {matches[0][0]}:\n")
        return matches[0][0]

    if len(matches) > 1:
        print(f"You searched for \"{player}\"\n{len(matches)} results found.")
        matches.sort(key=lambda tup: tup[1])
        # i = 0
        return matches[0][0]
        # for match in matches:
        #     print("{}: {}".format(i, match[0]))
        #     i += 1

        # selection = int(input("Pick one: "))
        # print("Results for {}:\n".format(matches[selection][0]))
        # return matches[selection][0]

    if len(matches) < 1:
        print(f"You searched for \"{player}\"\n{len(matches)} results found.")
        return ""

    print(f"You searched for \"{player}\"\n{len(matches)} result found.\n{matches[0][0]}")
    print(f"Results for {matches[0][0]}:\n")
    return matches[0][0]
