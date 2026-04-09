from src.merge import process_dataset, save_dataframe
from src.validate import load_schema, validate_dataframe



def run_pipeline():
    # Paths
    base_path = "data/raw"
    output_path = "D0_Data_Visualization/data/processed"
    schema = load_schema()

    # Enrolment
    enrol_df = process_dataset(
        f"{base_path}/enrolment",
        value_columns=["age_0_5", "age_5_17", "age_18_greater"]
    )
    enrol_df = validate_dataframe(enrol_df, "enrolment", schema)
    save_dataframe(enrol_df, f"{output_path}/enrolment_master.csv")

    # Demographic
    demo_df = process_dataset(
        f"{base_path}/demographic",
        value_columns=["demo_age_5_17", "demo_age_17_"]
    )
    demo_df = validate_dataframe(demo_df, "demographic", schema)
    save_dataframe(demo_df, f"{output_path}/demographic_master.csv")

    # Biometric
    bio_df = process_dataset(
        f"{base_path}/biometric",
        value_columns=["bio_age_5_17", "bio_age_17_"]
    )
    bio_df = validate_dataframe(bio_df, "biometric", schema)
    save_dataframe(bio_df, f"{output_path}/biometric_master.csv")


if __name__ == "__main__":
    run_pipeline()