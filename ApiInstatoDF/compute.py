#### ---- IMPORTS ---- ####
from ApiInstatoDF import get_urls_to_df, create_df, INGEST_DATE

### ---- MAIN COMPUTE FUNCION ---- ###


def compute():
    """
    Main function to run the program.
    """
    NAME = input("Enter the name of the profile: ")
    LEN = int(input("Enter the number of images to scrape: "))
    df_data = get_urls_to_df(NAME, LEN)
    df = create_df(df_data)
    # Save the DataFrame to a csv file.
    df.to_csv(f"{INGEST_DATE[:7]}-{NAME}.csv", index=False)
    print(df)


if __name__ == "__main__":
    compute()
