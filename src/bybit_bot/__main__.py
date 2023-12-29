import sys
import dotenv
dotenv.load_dotenv()


def main():
    from bybit_bot.app import App

    app = App()
    return app.run()


if __name__ == '__main__':
    sys.exit(main())
