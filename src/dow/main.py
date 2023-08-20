from dow.cli import cli
from dow.cli.utils import DowError, error

if __name__ == "__main__":
    try:
        cli.main()
    except DowError as e:
        error(str(e))
