import requests
from bs4 import BeautifulSoup

class ApiRequest():
    def __init__(self,model):
        self.url = "https://huggingface.co/models?pipeline_tag=text-generation&sort=trending"
        self.model = model
    def get_request(self):
        response = requests.get(self.url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            html_content = response.text
        else:
            html_content = None            
        return html_content
    def leader_models(self):
        html_content =self.get_request()
        
        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')

        # Find all elements with the specified class
        elements = soup.find_all('article', class_='overview-card-wrapper group/repo')
        dashboard_leaders = []
        # Extract values from the elements
        for element in elements:
            value = element.find('div').text
            model_name_dashboard= element.text.replace(value,"")
            model_name_dashboard= model_name_dashboard.replace("\n\n","")
            dashboard_leaders.append(model_name_dashboard)
        return dashboard_leaders
        
    def check_availibility(self):
        model_url =f"https://huggingface.co/{ self.model }?library=true"
        response = requests.get(model_url)
        return response.status_code 