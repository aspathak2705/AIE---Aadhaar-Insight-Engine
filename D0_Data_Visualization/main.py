from src.merge import process_dataset, save_dataframe


def run_pipeline():
    # Paths
    base_path = "data/raw"
    output_path = "D0_Data_Visualization/data/processed"

    # Enrolment
    enrol_df = process_dataset(
        f"{base_path}/enrolment",
        value_columns=["age_0_5", "age_5_17", "age_18_greater"]
    )
    save_dataframe(enrol_df, f"{output_path}/enrolment_master.csv")

    # Demographic
    demo_df = process_dataset(
        f"{base_path}/demographic",
        value_columns=["demo_age_5_17", "demo_age_17_"]
    )
    save_dataframe(demo_df, f"{output_path}/demographic_master.csv")

    # Biometric
    bio_df = process_dataset(
        f"{base_path}/biometric",
        value_columns=["bio_age_5_17", "bio_age_17_"]
    )
    save_dataframe(bio_df, f"{output_path}/biometric_master.csv")


if __name__ == "__main__":
    run_pipeline()