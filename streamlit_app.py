import streamlit as st

st.set_page_config(
    page_title="FPL League History",
    page_icon=":soccer:",
)

# Import functions
from src.app_utility.app_tools import (
    get_most_recent_august_start,
    remove_starting_the,
    generate_commentary,
)
from src.app_utility.create_output_tables import (
    get_team_and_league_data,
    get_team_and_league_data_filtered_summarised,
)

# Hide deploy button
st.markdown(
    r"""
    <style>
    .stDeployButton {
            visibility: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# Pre Processing
latest_season_start = get_most_recent_august_start()
import time


def main():
    try:
        st.title("FPL League History")
        st.markdown(
            "*[GitHub Repo](https://github.com/edward-farragher/ff-league-history)*"
        )

        # Input number
        league_id = st.number_input(
            "Enter League ID",
            step=1,
            format="%d",
            value=None,
            help="This is located in the league URL: `https://fantasy.premierleague.com/leagues/XXXXXX/standings/c`",
        )

        # Slider for another number
        season_start_year = st.slider(
            "Select League Starting Season",
            min_value=2000,
            max_value=latest_season_start,
            value=2002,
            step=1,
            help="Select the season start year to only select data after. For example if the league has only been running since a specific season, or there is a specific season where all teams were participation from",
        )

        # Button to trigger function execution
        if st.button("Generate League Data :soccer:"):
            st.write("")
            # Call your function with the input numbers

            # Get data

            with st.spinner(text="Getting league data..."):
                (
                    league_data,
                    manager_information,
                    team_ids,
                    final_gw_finished,
                    season_history,
                    season_current_df,
                    season_history_df,
                    current_gamekweek,
                    team_data,
                ) = get_team_and_league_data(league_id=int(league_id))

                (
                    league_name,
                    league_summary_kpis,
                    seasons_top_three_output,
                    titles_won_summary_output,
                    season_overview_output,
                    season_current_df_output,
                    season_history_df_output,
                    all_time_table_output,
                ) = get_team_and_league_data_filtered_summarised(
                    league_data=league_data,
                    manager_information=manager_information,
                    team_ids=team_ids,
                    season_current_df=season_current_df,
                    season_history_df=season_history_df,
                    season_start_year=season_start_year,
                    team_data=team_data,
                )

            number_of_teams = str(league_summary_kpis.loc["Number of teams"][0])
            year_start = str(league_summary_kpis.loc["Founded"][0])

            commentary = generate_commentary(
                league_name=league_name,
                number_of_teams=number_of_teams,
                year_start=year_start,
            )

            league_summary_kpis.reset_index(inplace=True)
            league_summary_kpis.columns = ["", league_name]
            # Display the output tables
            st.header(league_name, divider="grey")
            st.write(commentary)
            st.dataframe(data=league_summary_kpis, hide_index=True)

            st.subheader("Champions", divider="grey")
            st.dataframe(titles_won_summary_output, hide_index=True)

            st.subheader("List of Champions", divider="grey")
            st.dataframe(seasons_top_three_output, hide_index=True)

            league_name_starting_the_removed = remove_starting_the(text=league_name)
            st.subheader(f"All time {league_name_starting_the_removed}", divider="grey")
            st.dataframe(all_time_table_output, hide_index=True)

            st.subheader("Team Summary Statistics", divider="grey")
            st.dataframe(season_overview_output.T, hide_index=True)

            if final_gw_finished:
                season_current_df_output_dash_header = f"Current Season (Completed)"
            else:
                season_current_df_output_dash_header = (
                    f"Current Season (GW {current_gamekweek})"
                )

            st.subheader(season_current_df_output_dash_header, divider="grey")
            st.dataframe(season_current_df_output, hide_index=True)

            season_history_df_output_dash_header = (
                f"Previous {league_name_starting_the_removed} seasons"
            )
            st.subheader(f"{season_history_df_output_dash_header}", divider="grey")
            st.dataframe(season_history_df_output, hide_index=True)

    except Exception as e:
        st.error(
            """:lion_face: Unable to get league data. League ID is a number located in the league URL: `https://fantasy.premierleague.com/leagues/XXXXXX/standings/c`"""
        )


if __name__ == "__main__":
    main()
