import sys
import json


def createFBground(issueID, json_filename):
    '''
    returns two sets
        one with all cases with that issue (foreground)
        and one with all other cases (background)
    creates one JSON file labelled [issueID].json
        which includes a dictionary with two (key, value) pairs
        {'foreground':set of all foreground texts,
        'background': set of all background texts}
    '''
    background = []
    foreground = []
    with open(json_filename, 'r') as f:
        temp = json.load(f)
        for i in temp:
            if i == issueID:
                foreground = temp[i]
            else:
                background.extend(temp[i])

    # create foreground, background lists
    with open(f'{issueID}_foreground.list', 'w') as f:
        for case in foreground:
            f.write("cases/" + str(case) + ".txt\n")

    with open(f'{issueID}_background.list', 'w') as f:
        for case in background:
            f.write("cases/" + str(case) + ".txt\n")


if __name__ == "__main__":
    issueID = sys.argv[1]
    json_filename = sys.argv[2] + 'issues.json'
    createFBground(issueID, json_filename)
