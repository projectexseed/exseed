from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Post
from .forms import AddPostForm
from django.views import generic
from score.models import Point
from accounts.models import Account


def index(request):
    latest_post_list = Post.objects.filter(parent__isnull=True).order_by('-date_created')[:25]
    context = {
        'latest_post_list': latest_post_list,
    }
    return render(request, 'posts/index.html', context)


class DetailView(generic.DetailView):
    model = Post
    template_name = 'posts/detail.html'


class VoteToggleView(generic.View):
    def get(self, request, **kwargs):
        post_id = kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        if request.user.is_authenticated() and not post.votes.exists(request.user.id):
            post.votes.up(request.user.id)

            # We also want to make sure the user gets credit for the points.
            Point.objects.applyScore(post, 10)
        elif request.user.is_authenticated():
            post.votes.down(request.user.id)

            # We also want to make sure the user gets credit for the points.
            Point.objects.applyScore(post, -10)

        return JsonResponse({"new_vote_count": post.votes.count(), "did_vote": post.votes.exists(request.user.id)})


class ListByTag(generic.ListView):
    template_name = 'posts/tag_list.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        self.tag = self.kwargs.get('tag')
        """Return the last five published questions."""
        return Post.objects.filter(tags__slug__in=[self.tag]).order_by('-date_created')

    def get_context_data(self, **kwargs):
        context = super(ListByTag, self).get_context_data(**kwargs)
        context['tag'] = self.tag
        return context


class ListByUser(generic.ListView):
    template_name = 'posts/user_list.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        self.user = Account.objects.get(pk=user_id)
        return Post.objects.filter(owner__pk__in=[user_id]).order_by('-date_created')

    def get_context_data(self, **kwargs):
        context = super(ListByUser, self).get_context_data(**kwargs)
        context['user'] = self.user
        return context


class PostCreate(CreateView):
    model = Post
    form_class = AddPostForm

    def dispatch(self, *args, **kwargs):
        if kwargs.get('post_id'):
            self.parent_post = get_object_or_404(Post, pk=kwargs.get('post_id'))
        else:
            self.parent_post = None
        return super(PostCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.owner = self.request.user

        if self.parent_post:
            form.instance.parent = self.parent_post
            form.instance.ordinal = self.parent_post.next_ordinal()

        form.instance.save()
        return super(PostCreate, self).form_valid(form)


class PostUpdate(UpdateView):
    model = Post
    form_class = AddPostForm


class PostComplete(generic.View):
    def get(self, request, **kwargs):
        post_id = kwargs.get('post_id')
        try:
            post = Post.objects.get(pk=post_id)
            if post.owner == request.user:
                if post.completed:
                    post.completed = False
                else:
                    post.completed = True
                post.save()
                return JsonResponse({"completed": post.completed})
            else:
                raise Http404
        except Post.DoesNotExist:
            raise Http404


class PostReorderView(generic.View):
    def get(self, request, **kwargs):
        post_id = kwargs.get('post_id')
        parent_id = kwargs.get('parent_id')
        ordinal = int(kwargs.get('ordinal'))

        try:
            post = Post.objects.get(pk=post_id)
            parent_post = Post.objects.get(pk=parent_id)

            # Now go through and set the ordinals on all the children of the parent
            # and insert this one where it should go.
            replies = parent_post.replies.filter(ordinal__gte=ordinal).order_by('ordinal')

            x = ordinal + 1
            for reply in replies.all():
                reply.ordinal = x
                reply.save()
                x = x + 1

            # Set the new parent that the post was dragged over
            post.parent = parent_post
            post.ordinal = ordinal
            post.save()

            # Return ok
            return JsonResponse({"ok": "1"})
        except Post.DoesNotExist:
            raise Http404
#create
#update
#delete
#reply
#vote up
#vote down
#comment
#search
