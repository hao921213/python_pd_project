class CardSet:
    def __init__(self, cards):
        self.cards = sorted(cards, key=lambda card: card.get_number().value)
        self.set = {
            "Royal flush": 9,
            "Straight flush": 8,
            "Four of a kind": 7,
            "Full house": 6,
            "Flush": 5,
            "Straight": 4,
            "Three of a kind": 3,
            "Two pairs": 2,
            "One pair": 1,
            "High card": 0
        }

    def get_high(self, index):
        return self.cards[index].get_number().value

    def get_pairs(self):
        pairs = []
        i = 0
        while i < len(self.cards) - 1:
            if self.cards[i] and self.cards[i].get_number().value == self.cards[i + 1].get_number().value:
                pairs.append(self.cards[i])
                i += 1
            i += 1
        return len(pairs)

    def get_pairs_rank(self):
        max_rank = -1
        i = 0
        while i < len(self.cards) - 1:
            if self.cards[i] and self.cards[i].get_number().value == self.cards[i + 1].get_number().value:
                same_card_count = 1
                while i + same_card_count < len(self.cards) and self.cards[i + same_card_count].get_number().value == self.cards[i].get_number().value:
                    same_card_count += 1
                if same_card_count == 2:
                    max_rank = max(max_rank, self.cards[i].get_number().value)
                i += same_card_count - 1
            i += 1
        return max_rank

    def get_second_pairs_rank(self):
        max_rank = self.get_pairs_rank()
        second_max_rank = -1
        i = 0
        while i < len(self.cards) - 1:
            if self.cards[i] and self.cards[i].get_number().value == self.cards[i + 1].get_number().value and self.cards[i].get_number().value != max_rank:
                same_card_count = 1
                while i + same_card_count < len(self.cards) and self.cards[i + same_card_count].get_number().value == self.cards[i].get_number().value:
                    same_card_count += 1
                if same_card_count == 2:
                    second_max_rank = max(second_max_rank, self.cards[i].get_number().value)
                i += same_card_count - 1
            i += 1
        return second_max_rank

    def is_three_rank(self):
        for i in range(1, len(self.cards) - 1):
            if self.cards[i - 1] and self.cards[i].get_number().value == self.cards[i - 1].get_number().value and self.cards[i].get_number().value == self.cards[i + 1].get_number().value:
                return self.cards[i].get_number().value
        return -1

    def get_rank(self):
        if self.is_straight() and self.is_flush() and self.cards[-1].get_number().value == 14:
            return self.set["Royal flush"]
        elif self.is_straight() and self.is_flush():
            return self.set["Straight flush"]
        elif self.is_four():
            return self.set["Four of a kind"]
        elif self.is_three() and self.get_pairs() == 1:
            return self.set["Full house"]
        elif self.is_flush():
            return self.set["Flush"]
        elif self.is_straight():
            return self.set["Straight"]
        elif self.is_three():
            return self.set["Three of a kind"]
        elif self.get_pairs() == 2:
            return self.set["Two pairs"]
        elif self.get_pairs() == 1:
            return self.set["One pair"]
        else:
            return self.set["High card"]

    def is_straight(self):
        for i in range(4):
            if self.cards[i] and self.cards[i + 1] and self.cards[i].get_number().value + 1 != self.cards[i + 1].get_number().value:
                return False
        return True

    def is_flush(self):
        for i in range(4):
            if self.cards[i] and self.cards[i + 1] and self.cards[i].get_suit() != self.cards[i + 1].get_suit():
                return False
        return True

    def is_three(self):
        for i in range(1, len(self.cards) - 1):
            if self.cards[i - 1] and self.cards[i - 1].get_number().value == self.cards[i].get_number().value and self.cards[i].get_number().value == self.cards[i + 1].get_number().value:
                return True
        return False

    def is_four(self):
        count = 1
        for i in range(1, len(self.cards)):
            if self.cards[i] and self.cards[i].get_number().value == self.cards[i - 1].get_number().value:
                count += 1
                if count == 4:
                    return True
            else:
                count = 1
        return False

    def is_four_rank(self):
        count = 1
        for i in range(1, len(self.cards)):
            if self.cards[i] and self.cards[i].get_number().value == self.cards[i - 1].get_number().value:
                count += 1
                if count == 4:
                    return self.cards[i].get_number().value
            else:
                count = 1
        return -1
