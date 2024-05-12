from abc import ABC, abstractmethod
import random
import re
import requests
import time

BASE_URL = "https://challenge.crossmint.io/api/"
CANDIDATE_ID = "c1de9d5a-10c3-4e78-b52a-3d326898fcb8"

class point():
    def __init__(self, row, column) -> None:
        self.row = row
        self.column = column

class soloons_point(point):
    def __init__(self, row, column, color) -> None:
        self.color = color
        super().__init__(row, column)

class cometh_point(point):
    def __init__(self, row, column, direction) -> None:
        self.direction = direction
        super().__init__(row, column)


def retry_with_backoff(url, json, post, max_retries=5):
    retry_delay = 2
    
    for attempt in range(max_retries):
        request = None
        if post:
            request = requests.post(url, json=json)
        else:
            request = requests.delete(url, json=json)
        if request.status_code == 200:
            return
        time.sleep(retry_delay)
        retry_delay *= 2  # Double the delay for the next attempt
        retry_delay += random.uniform(0, 1)  # Add jitter

class megaverse_obj(ABC):
    def __init__(self, url) -> None:
        self.url = url
        self.points = []

    @abstractmethod
    def create_all(self):
        pass

    @abstractmethod
    def delete_all(self):
        pass

class Polyanets(megaverse_obj):
    def __init__(self) -> None:
        url = f'{BASE_URL}polyanets'
        super().__init__(url)
    
    def create_all(self):
        for point in self.points:
            obj = {'candidateId' : CANDIDATE_ID, 'row' : point.row, 'column' : point.column}
            retry_with_backoff(self.url, obj, True)

    def delete_all(self):
        for point in self.points:
            obj = {'candidateId' : CANDIDATE_ID, 'row' : point.row, 'column' : point.column}
            retry_with_backoff(self.url, obj, False)

class Soloons(megaverse_obj):
    def __init__(self) -> None:
        url = f'{BASE_URL}soloons'
        super().__init__(url)
    
    def create_all(self):
        for point in self.points:
            obj = {'candidateId' : CANDIDATE_ID, 'row' : point.row, 'column' : point.column, 'color' : point.color}
            retry_with_backoff(self.url, obj, True)

    def delete_all(self):
        for point in self.points:
            obj = {'candidateId' : CANDIDATE_ID, 'row' : point.row, 'column' : point.column}
            retry_with_backoff(self.url, obj, False)

class Comeths(megaverse_obj):
    def __init__(self) -> None:
        url = f'{BASE_URL}comeths'
        super().__init__(url)
    
    def create_all(self):
        for point in self.points:
            obj = {'candidateId' : CANDIDATE_ID, 'row' : point.row, 'column' : point.column, 'direction' : point.direction}
            retry_with_backoff(self.url, obj, True)

    def delete_all(self):
        for point in self.points:
            obj = {'candidateId' : CANDIDATE_ID, 'row' : point.row, 'column' : point.column}
            retry_with_backoff(self.url, obj, False)

def main():
    goal_url = f'{BASE_URL}map/{CANDIDATE_ID}/goal'
    goal = requests.get(goal_url).json()
    goal_map = goal['goal']
    polyanets = Polyanets()
    soloons = Soloons()
    comeths = Comeths()
    ROWS, COLS = len(goal_map), len(goal_map[0])

    for r in range(ROWS):
        for c in range(COLS):
            item = goal_map[r][c]
            if item == "POLYANET":
                polyanets.points.append(point(r, c))
            elif re.search("/*_SOLOON", item):
                soloons.points.append(soloons_point(r, c, item.split('_')[0].lower()))
            elif re.search("/*_COMETH", item):
                comeths.points.append(cometh_point(r, c, item.split('_')[0].lower()))
    
    polyanets.delete_all()
    comeths.delete_all()
    soloons.delete_all()
    polyanets.create_all()
    comeths.create_all()
    soloons.create_all()
     

if __name__ == "__main__":
    main()