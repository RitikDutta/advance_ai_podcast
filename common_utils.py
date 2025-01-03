import random

class CommonUtils:
    def _normalize_probabilities(self, probabilities):
        """
        Normalize probabilities to ensure they sum to 1.
        """
        total = sum(probabilities)
        return [p / total for p in probabilities] if total != 1 else probabilities

    def weighted_pick(self, numbers, probabilities):
        """
        Pick a number from the list based on specified probabilities.
        """
        probabilities = self._normalize_probabilities(probabilities)
        return random.choices(numbers, weights=probabilities, k=1)[0]

    def run_weighted_picker(self, numbers, probabilities):
        selected_number = self.weighted_pick(numbers, probabilities)
        print(f"Selected number: {selected_number}")

if __name__ == "__main__":
    numbers = [2, 5, 6, 7]
    probabilities = [0.2, 0.3, 0.25, 0.25]  # Corresponding probabilities
    utils = CommonUtils()
    utils.run_weighted_picker(numbers, probabilities)
