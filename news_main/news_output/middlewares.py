from .models import News, SubRubric
from datetime import datetime
from django.db.models import Q, Count


class RubricsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        return self.get_response(request)


    def process_template_response(self, request, response):
        if request.path.split("/")[1] == 'api':
            return response
        response.context_data['rubrics'] = SubRubric.objects.all()
        date = datetime.today()
        week = date.strftime("%V")
        response.context_data['news_week_more_views'] = News.objects.filter(published__week=week).annotate(active=Count('likedislike', filter=Q(likedislike__target_comment=None))).filter(active__gt=1)[:5]

        return response

