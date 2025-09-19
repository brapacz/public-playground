def model(dbt, session):

    dogs_df = dbt.ref("dogs")

    death_doctors = dict( )

    for doctor_name in dogs_df.filter(dogs_df["event type"] == "death").select("doctor's name"):
        death_doctors[doctor_name] = death_doctors.get(doctor_name, 0) + 1

    return [dict(doctor=doctor, death_count=count) for doctor, count in death_doctors.items()]
