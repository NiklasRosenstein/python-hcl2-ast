import argparse

from hcl2_ast.api import parse_file

parser = argparse.ArgumentParser()
parser.add_argument("file", type=argparse.FileType("r"))


def main() -> None:
    args = parser.parse_args()
    module = parse_file(args.file)
    print(module.pformat())


if __name__ == "__main__":
    main()
