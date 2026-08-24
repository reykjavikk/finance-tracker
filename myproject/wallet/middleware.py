import uuid
import time
from django.conf import settings
from django.http import HttpResponse


def request_info_middleware(get_response):



    def middleware(request):
        start_time = time.time()
        request.request_id = str(uuid.uuid4())
        request.start_time = start_time
        response = get_response(request)
        response['X-Request-ID'] = request.request_id
        response['X-Response-Time'] = f"{(time.time() - start_time) * 1000:.2f}ms"
        response['X-Server'] = "Django/Custom"
        print(f"{response['X-Request-ID']} {request.method} {request.path} - {response.status_code} - {response['X-Response-Time']}")
        return response


    return middleware


class BlockedUserAgentMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.blocked_users = getattr(settings, 'BLOCKED_USER_AGENTS', [])
        self.text = getattr(settings, 'BLOCKED_USER_AGENT_RESPONSE', 'Acces denied')

    def __call__(self, request):
        agent_name = self._get_user_agent(request)
        if self._is_user_agent_blocked(agent_name.lower()):
            return HttpResponse(self.text, status=403)
        response = self.get_response(request)
        response['X-User-Agent-Check'] = 'passed'
        return response

    def _get_user_agent(self, request):
        return request.META.get('HTTP_USER_AGENT', '')

    def _is_user_agent_blocked(self, name):
        for agent_name in self.blocked_users:
            if agent_name.lower() in name:
                return True
        return False


