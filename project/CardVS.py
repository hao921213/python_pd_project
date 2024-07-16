import itertools
from CardSet import CardSet

class CardVS:
    def card_vs(self, p1, p2, community_cards):
        max1 = self.get_max_rank(p1, community_cards)
        max2 = self.get_max_rank(p2, community_cards)
        maxset1 = self.get_max_rank_card_set(p1, community_cards)
        maxset2 = self.get_max_rank_card_set(p2, community_cards)

        if max1 > max2:
            return 1
        elif max2 > max1:
            return 2
        else:
            return self.tie_breaker(max1, maxset1, maxset2)

    def tie_breaker(self, max_rank, maxset1, maxset2):
        tie_breakers = {
            0: self.high_card_vs,
            1: self.one_pairs_vs,
            2: self.two_pair_vs,
            3: self.three_of_a_kind_vs,
            4: self.straight_vs,
            5: self.flush_vs,
            6: self.full_house_vs,
            7: self.four_of_a_kind_vs,
            8: self.straight_flush_vs,
            9: self.royal_flush_vs,
        }

        if max_rank in tie_breakers:
            return tie_breakers[max_rank](maxset1, maxset2)
        return -1

    def get_max_rank(self, player, community_cards):
        if not player or not community_cards:
            raise ValueError("Player and community cards cannot be null")

        if len(community_cards) < 5:
            raise ValueError("Community cards must have at least 5 cards")

        max_rank = 0
        all_cards = player.get_hand() + community_cards

        for hand in itertools.combinations(all_cards, 5):
            set = CardSet(hand)
            max_rank = max(max_rank, set.get_rank())

        return max_rank

    def get_max_rank_card_set(self, player, community_cards):
        if not player or not community_cards:
            raise ValueError("Player and community cards cannot be null")

        if len(community_cards) < 5:
            raise ValueError("Community cards must have at least 5 cards")

        max_rank = 0
        max_rank_set = None
        all_cards = player.get_hand() + community_cards

        for hand in itertools.combinations(all_cards, 5):
            set = CardSet(hand)
            rank = set.get_rank()
            if rank > max_rank:
                max_rank = rank
                max_rank_set = set

        return max_rank_set

    def high_card_vs(self, maxset1, maxset2):
        for i in range(4, -1, -1):
            if maxset1.get_high(i) > maxset2.get_high(i):
                return 1
            elif maxset1.get_high(i) < maxset2.get_high(i):
                return 2
        return 0

    def one_pairs_vs(self, maxset1, maxset2):
        if maxset1.get_pairs_rank() > maxset2.get_pairs_rank():
            return 1
        elif maxset1.get_pairs_rank() < maxset2.get_pairs_rank():
            return 2
        else:
            return self.high_card_vs(maxset1, maxset2)

    def two_pair_vs(self, maxset1, maxset2):
        if maxset1.get_pairs_rank() > maxset2.get_pairs_rank():
            return 1
        elif maxset1.get_pairs_rank() < maxset2.get_pairs_rank():
            return 2
        else:
            if maxset1.get_second_pairs_rank() > maxset2.get_second_pairs_rank():
                return 1
            elif maxset1.get_second_pairs_rank() < maxset2.get_second_pairs_rank():
                return 2
            else:
                return self.high_card_vs(maxset1, maxset2)

    def three_of_a_kind_vs(self, maxset1, maxset2):
        if maxset1.is_three_rank() > maxset2.is_three_rank():
            return 1
        elif maxset1.is_three_rank() < maxset2.is_three_rank():
            return 2
        else:
            return self.high_card_vs(maxset1, maxset2)

    def straight_vs(self, maxset1, maxset2):
        return self.high_card_vs(maxset1, maxset2)

    def flush_vs(self, maxset1, maxset2):
        return self.high_card_vs(maxset1, maxset2)

    def full_house_vs(self, maxset1, maxset2):
        if self.three_of_a_kind_vs(maxset1, maxset2) != 0:
            return self.three_of_a_kind_vs(maxset1, maxset2)
        else:
            return self.one_pairs_vs(maxset1, maxset2)

    def four_of_a_kind_vs(self, maxset1, maxset2):
        if maxset1.is_four_rank() > maxset2.is_four_rank():
            return 1
        elif maxset1.is_four_rank() < maxset2.is_four_rank():
            return 2
        else:
            return self.high_card_vs(maxset1, maxset2)

    def straight_flush_vs(self, maxset1, maxset2):
        return self.high_card_vs(maxset1, maxset2)

    def royal_flush_vs(self, maxset1, maxset2):
        return self.high_card_vs(maxset1, maxset2)
