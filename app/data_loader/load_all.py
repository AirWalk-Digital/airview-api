from . import load_applications, load_base


def load():
    print("Loading All...")
    load_base.load()
    load_applications.load()


if __name__ == "__main__":
    load()
