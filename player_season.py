import pandas as pd


class PlayerSeason:

    def __init__(self, list_of_week_dicts):

        self.stats = pd.DataFrame(list_of_week_dicts, index=range(1, 18))
        stats = self.stats
        stats['points'] = 0.1 * (stats['Rush_Yds'] + stats['Rec_Yds']) + 6 * (
            stats['Rush_TD'] + stats['Rec_TD']) + 0.04 * stats['Pass_Yds'] + \
            4 * stats['Pass_TD'] - 2 * (stats['Fum_Lost'] + stats['Int'])
        self.total_points = stats['points'].sum()
