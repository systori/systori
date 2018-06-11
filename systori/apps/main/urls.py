from django.conf.urls import url
from ..user.authorization import office_auth
from .views import (
    IndexView,
    DayBasedOverviewView,
    NotesDashboard,
    NoteUpdateView,
    NoteDeleteView,
)

urlpatterns = [
    url(r"^$", IndexView.as_view(), name="home"),
    url(
        r"^day-based-overview/(?P<selected_day>\d{4}-\d{2}-\d{2})?$",
        office_auth(DayBasedOverviewView.as_view()),
        name="day_based_overview",
    ),
    url(r"^notes$", office_auth(NotesDashboard.as_view()), name="notes"),
    url(r"^note-(?P<pk>\d+)$", office_auth(NoteUpdateView.as_view()), name="note"),
    url(
        r"^note-(?P<pk>\d+)(?P<success_url>/\w+-\d+)$",
        office_auth(NoteUpdateView.as_view()),
        name="note",
    ),
    url(
        r"^note-(?P<pk>\d+)/delete$",
        office_auth(NoteDeleteView.as_view()),
        name="note.delete",
    ),
    url(
        r"^note-(?P<pk>\d+)(?P<success_url>/\w+-\d+)/delete$",
        office_auth(NoteDeleteView.as_view()),
        name="note.delete",
    ),
]
