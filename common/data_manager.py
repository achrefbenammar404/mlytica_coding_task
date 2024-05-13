import json
import os

class DataManager:
    def __init__(self, file_path="competition_results.txt"):
        self.file_path = file_path
        self.data_cache = None
        self.last_read_timestamp = None

    def read_competition_results(self):
        try:
            current_timestamp = os.path.getmtime(self.file_path)
            if self.data_cache is None or self.last_read_timestamp != current_timestamp:
                with open(self.file_path, 'r') as file:
                    data = file.readlines()
                results = {}
                for line in data:
                    place, employee, department = line.strip().split(',')
                    results[place.strip()] = {"employee": employee.strip(), "department": department.strip()}
                self.data_cache = results
                self.last_read_timestamp = current_timestamp
            return self.data_cache
        except (FileNotFoundError, PermissionError) as e:
            # Handle file operation errors
            print(f"Error reading competition results: {e}")
            return {}
