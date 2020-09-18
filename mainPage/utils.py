from ip2geotools.databases.noncommercial import DbIpCity


class utlity:
    def __init__(self):
        super().__init__()

    def get_client_ip_address(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_user_agent(self, request):
        return request.META['HTTP_USER_AGENT']

    def get_location_via_ip(self, ip_addr):
        try:
            response = DbIpCity.get(str(ip_addr), api_key='free')
            location = {"city": response.city, "region":response.region, "country":response.country}
            return location
        except:
            return None