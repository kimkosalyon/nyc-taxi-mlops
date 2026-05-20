# https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-01.parquet
import datetime
from pathlib import Path
from urllib.request import urlretrieve
import httpx
import click
from tqdm import tqdm
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
# yellow, green supported for now
SUPPORTED_TAXI_TYPES = ["yellow", "green"]
BRONZE_DIR = Path("data/bronze")

# NO MAGIC NUMBER
CHUNK_SIZE = 8192  # 8 KB
HTTPX_TIMEOUT = 10.0  # seconds

def build_filename(taxi_type: str, year: int, month: int) -> str:
    # :02d = zero-padded 2 digit integer. E.g. 1 becomes "01", 10 stays "10"
    return f"{taxi_type}_tripdata_{year}-{month:02d}.parquet"


def build_url(taxi_type: str, year: int, month: int) -> str:
    """
    Build the URL to download the taxi data for the given parameters. 
    """ 
    filename = build_filename(taxi_type=taxi_type, year=year, month=month)
    return f"{BASE_URL}/{filename}"

def fetch_file(taxi_type: str, year: int, month: int) -> Path:
    """
    Fetch the taxi data file for the given parameters and save it to the bronze directory. 
    Returns the path to the downloaded file.
    """ 
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)  # Create the bronze directory if it doesn't exist
    url = build_url(taxi_type=taxi_type, year=year, month=month)
    filename = build_filename(taxi_type=taxi_type, year=year, month=month)
    output_path = BRONZE_DIR / filename
    
    
    with httpx.stream("GET", url, timeout=HTTPX_TIMEOUT) as response:
        response.raise_for_status()  # Check if the request was successful
        total_size = int(response.headers.get("Content-Length", 0))
        
        with tqdm(total=total_size, unit="B", unit_scale=True, desc=filename) as progress_bar:
            with open(output_path, "wb") as output_file:
                for chunk in response.iter_bytes(chunk_size=CHUNK_SIZE):
                    output_file.write(chunk)
                    progress_bar.update(len(chunk))
               
    return output_path


# now write args
@click.command()
@click.option("--taxi-type", required=True, type=click.Choice(choices=SUPPORTED_TAXI_TYPES, case_sensitive=False), help="The type of taxi data to fetch (yellow or green).")
@click.option("--year", required=True, type=int, help="The year of the taxi data to fetch.", show_default=True)
@click.option("--month", required=True, type=click.IntRange(1, 12), help="The month of the taxi data to fetch.")
@click.option(
    "--overwrite",
    is_flag=True,
    help="Overwrite the file if it already exists.",
)
def main(taxi_type: str, year: int, month: int, overwrite: bool):
    print(f"Fetching {taxi_type} taxi data for {month}/{year}...")
    
    if not overwrite and output_path.exists():
        click.echo(f"File already exists at {output_path}. Use --overwrite to overwrite it.")
        return
    
    output_path = fetch_file(taxi_type=taxi_type, year=year, month=month)

    click.echo(f"File saved to: {output_path}")    
    
if __name__ == "__main__":
    main()
   