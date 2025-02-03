from bot.vk_apis.bot import VkBot

if __name__ == "__main__":
    bot = VkBot()
    # Debug print the riddles
    print("Loaded riddles:", bot.config.riddles)
    try:
        bot.run()
    except KeyboardInterrupt:
        bot.shutdown_event.set()
        print("\nBot stopped gracefully") 