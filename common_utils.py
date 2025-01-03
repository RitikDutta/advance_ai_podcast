import random

class WeightedPicker:
    def __init__(self, numbers, probabilities):
        self.numbers = numbers
        self.probabilities = self._normalize_probabilities(probabilities)

    def _normalize_probabilities(self, probabilities):
        """
        Normalize probabilities to ensure they sum to 1.
        """
        total = sum(probabilities)
        return [p / total for p in probabilities] if total != 1 else probabilities

    def pick(self):
        """
        Pick a number from the list based on specified probabilities.
        """
        return random.choices(self.numbers, weights=self.probabilities, k=1)[0]

    def pick(self):
        selected_number = self.pick()
        print(f"Selected number: {selected_number}")

if __name__ == "__main__":
    numbers = ['sip_coffee', 'nod', 'yes long', 'fill']
    probabilities = [0.10, 0.10, 0.10, 0.70]  # Corresponding probabilities
    picker = WeightedPicker(numbers, probabilities)
    picker.pick()
