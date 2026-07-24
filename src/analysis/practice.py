import pandas as pd


def best_time_treningu(session):
    """
    Tworzy tabele z najszybszymi czasami okrazen i gapem do lidera
    dla danej sesji treningowej.
    """
    najlepsze = session.laps.groupby('Driver')['LapTime'].min()
    najlepsze = najlepsze.sort_values()
    gaptobest = najlepsze - najlepsze.iloc[0]

    def ladne_czasy(t):
        s = t.total_seconds()
        m = int(s // 60)
        sec = s % 60
        return f'{m}:{sec:06.3f}'

    najlepsze_ladne = najlepsze.apply(ladne_czasy)
    gaptobest_ladne = gaptobest.apply(ladne_czasy)

    wyniki = pd.DataFrame({
        'Kierowca': najlepsze.index,
        'NajlepszyCzas': najlepsze_ladne.values,
        'Gap': gaptobest_ladne.values
    })

    return wyniki