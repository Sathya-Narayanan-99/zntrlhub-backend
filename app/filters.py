from dj_rql.filter_cls import AutoRQLFilterClass

from app.models import Analytics


class AnalyticsFilters(AutoRQLFilterClass):
    MODEL = Analytics
