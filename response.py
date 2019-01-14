from duplicates import Duplicates

class Response:

    def __init__(self):
        self.duplicates = Duplicates()
        self.responses = None
    
    def set_responses(self, responses):
        self.responses = responses
        self.duplicates.set_results(responses)

    def get_reponses(self):
        return self.responses

    def remove_duplicates(self):
        self.duplicates.remove_duplicates()
        self.set_responses(self.duplicates.get_results())

