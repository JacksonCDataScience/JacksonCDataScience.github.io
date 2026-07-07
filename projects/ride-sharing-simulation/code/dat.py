def real_kpi_vals(df_drivers, df_riders):
    # find abandon rates (dont include trips that are not completed)
    ab_count = sum(df_riders["status"] == "abandoned")
    comp_count = sum(df_riders["status"] == "dropped-off")
    ar = ab_count / (ab_count + comp_count)

    # calculate wait times
    completed = df_riders[df_riders["status"] == "dropped-off"]
    wait_times = completed["pickup_time"] - completed["request_time"]

    # the kpis we are able to find given the datasets given
    real_kpis = {
        "abandon_rates": ar,
        "wait_times": wait_times
    }
    return real_kpis