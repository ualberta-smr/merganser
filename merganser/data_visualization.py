
import matplotlib.pyplot as plt

import config
from  data_retrieval import Data_Retreival

class Visualization:
    def __init__(self):
        self.data_retreival = Data_Retreival()
        self.conflict_ratio = self.data_retreival.get_conflict_ratio()

    def vis_scenarios_conflict_num(self):
        plt.figure()
        plt.bar(self.conflict_ratio['Repository Name'], self.conflict_ratio['# Merge Scenarios'])
        plt.bar(self.conflict_ratio['Repository Name'], self.conflict_ratio['# Merge Scenarios with Conflicts'])
        plt.title('Merge Scenarios and Conflict Ratio')
        plt.xlabel('Repository Name')
        plt.ylabel('# Scenarios')
        plt.xticks(rotation=90)
        plt.legend(['# Merge Scenarios', '# Merge Scenarios with Conflicts'])
        plt.show()
        plt.close()

    def vis_conflict_ratio_hist(self):
        plt.figure()
        plt.hist(self.conflict_ratio['Conflict Rate (%)'])
        plt.title('Conflict Ratio Histogram')
        plt.xlabel('# Merge Scenarios with Conflicts')
        plt.ylabel('Ratio')
        plt.xticks(rotation=90)
        plt.legend(['# Merge Scenarios', '# Merge Scenarios with Conflicts'])
        plt.show()
        plt.close()

vis = Visualization()
vis.vis_scenarios_conflict_num()