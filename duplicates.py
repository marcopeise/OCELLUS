from pprint import pprint

class Duplicates:

    def set_results(self, results):
        self.results = results

    def get_results(self):
        return self.results

    # very simple approach to deleting duplicates by checking for dupilcate doi's
    def remove_duplicates(self):
        added_elements = set()
        res_without_duplicates = []
        removed_entries = 0
        for entry in self.results:
            if entry['doi'] not in added_elements:
                added_elements.add(entry['doi'])
                res_without_duplicates.append(entry)
            else:
                removed_entries += 1
        print("\n\n# Removing duplicates #")
        print("  -Total entries: " + str(removed_entries + len(res_without_duplicates)))
        print("  -Removed entries: " + str(removed_entries))
        print("  -Remaining entries: " + str(len(res_without_duplicates)))

        self.set_results(res_without_duplicates)
            
