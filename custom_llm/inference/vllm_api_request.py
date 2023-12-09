import requests
from bs4 import BeautifulSoup

class SupportedModelsScraper:
    def __init__(self):
        self.url = "https://docs.vllm.ai/en/latest/models/supported_models.html"
        self.data = []

    def scrape_data(self):
        # Send an HTTP GET request to the URL
        response = requests.get(self.url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, "html.parser")

            # Find the section of the page containing the supported models
            supported_models_section = soup.find("section", {"id": "supported-models"})

            # Check if the supported models section is found
            if supported_models_section:
                # Find the tbody element within the supported models section
                tbody = supported_models_section.find("tbody")

                # Check if the tbody element is found
                if tbody:
                    # Find all table rows within the tbody
                    rows = tbody.find_all("tr")

                    # Extract and store information from each row
                    for row in rows:
                        # Extract data from specific cells in the row if needed
                        cells = row.find_all("td")  # Assuming the data is in <td> elements
                        data = [cell.get_text() for cell in cells]
                        self.data.append(data)
                else:
                    print("tbody element not found within the supported models section.")
            else:
                print("Supported models section not found on the page.")
        else:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

    def get_data(self):
        flat_list = []
        for row in self.data:
            flat_list.extend(row)
        return flat_list

