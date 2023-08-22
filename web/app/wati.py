import requests

class Wati:
    def __init__(self, api_endpoint, api_key):
        self.api_endpoint = api_endpoint
        self.api_key = api_key

    def _get_headers(self):
        return {
            "Authorization": self.api_key
        }

    def get_templates(self, page_size=500, page_number=1):
        url = f"{self.api_endpoint}/api/v1/getMessageTemplates"
        params = {
            "pageSize": page_size,
            "pageNumber": page_number
        }
        try:
            res = requests.get(url, params=params, headers=self._get_headers(), timeout=90)
            res.raise_for_status()
        except Exception as exc:
            # TODO: Handle exceptions
            print(str(exc))
            raise exc
        templates = res.json().get('messageTemplates')
        return templates

    def get_messages_for_number(self, number, page_size=100, page_number=1):
        url = f"{self.api_endpoint}/api/v1/getMessages/{number}"
        params = {
            "pageSize": page_size,
            "pageNumber": page_number
        }
        try:
            res = requests.get(url, params=params, headers=self._get_headers(), timeout=90)
            res.raise_for_status()
        except Exception as exc:
            # TODO: Handle exceptions
            print(str(exc))
            raise exc
        messages = res.json()
        return messages

    def send_tempate_messages(self, template_name, broadcast_name, recievers):
        url = f"{self.api_endpoint}/api/v1/sendTemplateMessages"
        payload = {
            "template_name": template_name,
            "broadcast_name": broadcast_name,
            "receivers": recievers
        }
        try:
            res = requests.post(url, headers=self._get_headers(), json=payload, timeout=90)
            res.raise_for_status()
        except Exception as exc:
            # TODO: Handle exceptions
            print(str(exc))
            raise exc
        return res.json()

    def get_connection_status(self):
        url = f"{self.api_endpoint}/api/v1/getContacts"
        try:
            res = requests.get(url, headers=self._get_headers(), timeout=90)
            res.raise_for_status()
            return True
        except Exception as exc:
            print(str(exc))
            return False
