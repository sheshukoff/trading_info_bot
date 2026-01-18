class Reports:
    def __init__(self):
        self.users = {}
        self.strategies = {}

    def add_user_strategy(self, chat_id, strategy, coin, timeframe):
        value = f'{strategy}|{coin}|{timeframe}'
        if chat_id not in self.users:
            self.users[chat_id] = [value]
        else:
            self.users[chat_id].append(value)

        name_strategy = f'{strategy}|{coin}|{timeframe}'
        if name_strategy not in self.strategies:
            self.strategies[name_strategy] = [chat_id]
        else:
            self.strategies[name_strategy].append(chat_id)

    def get_user_strategies(self, chat_id: int):
        return self.users.get(chat_id, [])

    def get_strategy_users(self, strategy):
        return self.strategies.get(strategy, [])

    def remove_user_strategy(self, chat_id, strategy):
        if chat_id in self.users:
            if strategy in self.users.get(chat_id):
                self.users[chat_id].remove(strategy)

                if not self.users.get(chat_id):
                    del self.users[chat_id]

        if strategy in self.strategies:
            if chat_id in self.strategies.get(strategy):
                self.strategies[strategy].remove(chat_id)

                if not self.strategies.get(strategy):
                    del self.strategies[strategy]


reports = Reports()
