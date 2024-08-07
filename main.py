import sys
import json


def parse_json(json_string):
    print("Printing json content")
    print(json.loads(json_string))


if __name__ == "__main__":
    parse_json(sys.argv[1])
