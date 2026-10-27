"""Cached, measured warehouse overview with compact navy chart panels."""
from pathlib import Path
import duckdb
import streamlit as st


@st.cache_data(ttl=60)
def read_overview(path: str, modified: float) -> dict:
    """Read related aggregates together and always close the database connection."""
    with duckdb.connect(path, read_only=True) as con:
        counts = con.execute('SELECT count(*), min(date_key), max(date_key) FROM fact_events').fetchone()
        repos = con.execute('SELECT count(*) FROM dim_repo').fetchone()[0]
        actors = con.execute('SELECT count(*) FROM dim_actor').fetchone()[0]
        stars = con.execute('SELECT coalesce(sum(star_count),0) FROM agg_stars_per_repo_day').fetchone()[0]
        top = con.execute('SELECT repo_name, sum(star_count) AS stars FROM agg_stars_per_repo_day GROUP BY repo_name ORDER BY stars DESC LIMIT 8').fetchdf()
        traffic = con.execute('''SELECT hour, count(*) AS events FROM fact_events GROUP BY hour ORDER BY hour''').fetchdf()
        kinds = con.execute('''SELECT e.event_type, count(*) AS events FROM fact_events f JOIN dim_event_type e
            ON f.event_type_key=e.event_type_key GROUP BY e.event_type ORDER BY events DESC''').fetchdf()
        active = con.execute('''SELECT r.repo_name, count(*) AS events FROM fact_events f JOIN dim_repo r
            ON f.repo_key=r.repo_key GROUP BY r.repo_name ORDER BY events DESC LIMIT 8''').fetchdf()
    return dict(counts=counts, repos=repos, actors=actors, stars=stars, top=top,
                traffic=traffic, kinds=kinds, active=active)


def render(db_path: Path) -> None:
    """Show four headline metrics and focused charts from the actual database."""
    st.subheader('Activity overview')
    st.write('Explore recorded GitHub activity, popular repositories, and hourly event volume.')
    if not db_path.exists():
        st.warning('No local or demo warehouse found.')
        return
    data = read_overview(str(db_path), db_path.stat().st_mtime)
    count, first, last = data['counts']
    def date_label(value) -> str:
        text = str(value)
        return f'{text[:4]}-{text[4:6]}-{text[6:]}'
    st.caption(f"Data: GH Archive · {date_label(first)} to {date_label(last)} · {count:,} events · {db_path.name}")
    for col, label, value in zip(st.columns(4), ('Events','Repositories','Developer IDs','Stars recorded'),
                                  (count,data['repos'],data['actors'],data['stars'])):
        col.metric(label, f'{value:,}')
    left, right = st.columns([3,2])
    with left, st.container(border=True):
        st.markdown('#### Activity by hour (UTC)')
        st.area_chart(data['traffic'].set_index('hour'), color='#46c6ef', height=260,
                      x_label='Hour of day (UTC)', y_label='Events across selected source days')
    with right, st.container(border=True):
        st.markdown('#### Event composition')
        st.bar_chart(data['kinds'].set_index('event_type'), horizontal=True, color='#9483ff',
                     height=260, sort='-events', x_label='Events', y_label='Event type')
    left, right = st.columns(2)
    with left, st.container(border=True):
        st.markdown('#### Most starred repositories')
        st.bar_chart(data['top'].set_index('repo_name'), horizontal=True, color='#46c6ef',
                     height=300, sort='-stars', x_label='Recorded star events', y_label='Repository')
    with right, st.container(border=True):
        st.markdown('#### Most active repositories')
        st.dataframe(data['active'], hide_index=True, width='stretch')
