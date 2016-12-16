from django.contrib.auth.decorators import login_required
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='post_index'),
    url(r'^create/$', login_required(views.PostCreate.as_view()), name='post_create'),
    url(r'^update/(?P<pk>[0-9]+)/$', login_required(views.PostUpdate.as_view()), name='post_update'),
    url(r'^create/(?P<post_id>[0-9]+)/$', login_required(views.PostCreate.as_view()), name='post_reply'),
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='post_detail'),
    url(r'^complete/$', views.PostComplete.as_view(), name='post_complete_ajax_template'),
    url(r'^complete/(?P<post_id>[0-9]+)/$', views.PostComplete.as_view(), name='post_complete'),
    url(r'^tag/(?P<tag>[\w\-]+)/$', views.ListByTag.as_view(), name='post_list_by_tag'),
    url(r'^user/(?P<user_id>[\w\-]+)/$', views.ListByUser.as_view(), name='post_list_by_user'),
    url(r'^vote/$', views.VoteToggleView.as_view(), name='post_vote_toggle_ajax_template'),
    url(r'^vote/(?P<post_id>[0-9]+)/$', views.VoteToggleView.as_view(), name='post_vote_toggle'),
    url(r'^reorder/$', views.PostReorderView.as_view(), name='post_reorder_ajax_template'),
    url(r'^reorder/(?P<post_id>[0-9]+)/(?P<parent_id>[0-9]+)/(?P<ordinal>[0-9]+)/$', views.PostReorderView.as_view(), name='post_reorder'),
]
