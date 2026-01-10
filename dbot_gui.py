# main.py

from bot.engine import DBot  # your existing bot imports

def start_dbot():
    bot = DBot()
    bot.run()  # or whatever your bot uses to start

# Optional: allow running directly
if __name__ == "__main__":
    start_dbot()
