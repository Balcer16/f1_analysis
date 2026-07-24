#%%
import pandas as pd
import fastf1
session=fastf1.get_session(2026,"Belgium","FP1")
session.load()
najlepsze = session.laps.groupby('Driver')['LapTime'].min()
najlepsze=najlepsze.sort_values()

gaptobest= najlepsze- najlepsze.iloc[0]

# %%
def ladne_czasy(Timedelta):
    s=Timedelta.total_seconds()
    m = int(s // 60)
    sec = s % 60
    return f'{m}:{sec:06.3f}'
najlepsze_ladne=najlepsze.apply(ladne_czasy)
najlepsze_ladne
gaptobest_ladne=gaptobest.apply(ladne_czasy)
gaptobest_ladne
# %%
wyniki = pd.DataFrame({
    'Kierowca': najlepsze.index,
    'NajlepszyCzas': najlepsze_ladne.values,
    'Gap': gaptobest_ladne.values
})
wyniki
# %%
def best_time_treningu(session):
    """
    Tworzy tabele z najszybszymi czasami okrazen i gapem do lidera
    dla danej sesji treningowej.
    """
    najlepsze = session.laps.groupby('Driver')['LapTime'].min()
    najlepsze=najlepsze.sort_values()
    gaptobest= najlepsze- najlepsze.iloc[0]
    def ladne_czasy(Timedelta):
        s=Timedelta.total_seconds()
        m = int(s // 60)
        sec = s % 60
        return f'{m}:{sec:06.3f}'
    najlepsze_ladne=najlepsze.apply(ladne_czasy)
    gaptobest_ladne=gaptobest.apply(ladne_czasy)
    wyniki = pd.DataFrame({
        'Kierowca': najlepsze.index,
        'NajlepszyCzas': najlepsze_ladne.values,
        'Gap': gaptobest_ladne.values
    })

    return wyniki
# %%
best_time_treningu(session)
# %%
import sys
import os
sys.path.append(os.path.abspath('..'))

from src.analysis.practice import best_time_treningu
# %%
wyniki = best_time_treningu(session)
wyniki
# %%
grupy = session.laps.groupby(['Driver', 'Stint']).size()
dlugie_stinty = grupy[grupy > 5]
dlugie_stinty
# %%
dlugie_okrazenia = session.laps.groupby(['Driver', 'Stint']).filter(lambda x: len(x) > 5)
# %%
len(dlugie_okrazenia)

# %%
len(session.laps)
# %%
dlugie_okrazenia['Driver'].unique()
# %%
laps_clean = session.laps[session.laps['PitInTime'].isna() & session.laps['PitOutTime'].isna()]
dlugie_okrazenia = laps_clean.groupby(['Driver', 'Stint']).filter(lambda x: len(x) > 3)
len(dlugie_okrazenia)
tempo_stintow = dlugie_okrazenia.groupby(['Driver', 'Stint'])['LapTime'].mean()
tempo_stintow=tempo_stintow.sort_values()
tempo_stintow=tempo_stintow.apply(ladne_czasy)
tempo_stintow
# %%
import plotly.express as px

# Przygotowanie danych
dlugie_okrazenia['LapTimeSeconds'] = dlugie_okrazenia['LapTime'].dt.total_seconds()
dlugie_okrazenia['LapTime_dt'] = pd.to_datetime(dlugie_okrazenia['LapTimeSeconds'], unit='s')

# Kolejność kierowców na osi X - od najszybszej mediany do najwolniejszej
kolejnosc = dlugie_okrazenia.groupby('Driver')['LapTimeSeconds'].median().sort_values().index.tolist()

fig = px.box(
    dlugie_okrazenia,
    x='Driver', y='LapTime_dt', color='Compound',
    category_orders={'Driver': kolejnosc},
    template='plotly_dark',
    title='Long run pace - rozkład czasów okrążeń'
)
fig.update_yaxes(tickformat='%M:%S.%L')
fig.update_layout(width=1100, height=550)

fig.show()
# %%

import plotly.graph_objects as go
import fastf1.plotting

# KROK 1: Podstawowe filtry (zostawiamy jako pierwsza linia obrony)
laps_do_analizy = dlugie_okrazenia[
    (dlugie_okrazenia['TrackStatus'] == '1') &
    (dlugie_okrazenia['IsAccurate'] == True)
].copy()
laps_do_analizy['LapTimeSeconds'] = laps_do_analizy['LapTime'].dt.total_seconds()

# KROK 2: Usuwamy anomalie per stint - max 15% wolniej niz wlasny najszybszy czas w danym stincie
def usun_anomalie(grupa):
    najszybsze = grupa['LapTimeSeconds'].min()
    return grupa[grupa['LapTimeSeconds'] < najszybsze * 1.15]

laps_do_analizy = laps_do_analizy.groupby(['Driver', 'Stint'], group_keys=False).apply(usun_anomalie)
laps_do_analizy['LapTime_dt'] = pd.to_datetime(laps_do_analizy['LapTimeSeconds'], unit='s')

# KROK 3: Osobny wykres dla kazdej mieszanki
for compound in laps_do_analizy['Compound'].unique():
    subset = laps_do_analizy[laps_do_analizy['Compound'] == compound]
    kolejnosc = subset.groupby('Driver')['LapTimeSeconds'].mean().sort_values().index.tolist()

    fig = go.Figure()
    for driver in kolejnosc:
        driver_data = subset[subset['Driver'] == driver]
        color = fastf1.plotting.get_driver_color(driver, session=session)
        fig.add_trace(go.Box(
            y=driver_data['LapTime_dt'],
            name=driver,
            marker_color=color,
            boxmean=True,
        ))

    fig.update_yaxes(tickformat='%M:%S.%L', gridcolor='rgba(255,255,255,0.15)')
    fig.update_layout(
        title=f'Long run pace - mieszanka {compound}',
        yaxis_title='Czas okrążenia',
        template='plotly_dark',
        showlegend=False,
        width=1100, height=550,
    )
    fig.show()
# %%
