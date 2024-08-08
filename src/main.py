import sys
import json


def parse_json(json_string):
    print("Printing json content")
    print(json.dumps(json_string))


if __name__ == "__main__":
    print(sys.argv)
    parse_json({"Hi": "Hello"})
