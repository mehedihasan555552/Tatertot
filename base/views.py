from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib import messages

from .models import Show, Episode, AppSettings
from .forms import ShowForm, EpisodeForm, AppSettingsForm, PublishForm, LoginForm
from .roku import *
from .firetv import *
from django.urls import reverse

def login_view(request):
    """Login view"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})



def userlogout(request):
    logout(request)
    return redirect('login')



@login_required
def dashboard(request):
    """Main dashboard view to display shows and episodes"""
    shows = Show.objects.prefetch_related('episodes').order_by('order')
    
    context = {
        'shows': shows,
        'episode_form': EpisodeForm(),
        'show_form': ShowForm(),
        'edit_mode': False,
        'form_action_url': reverse('add_episode', args=[shows.first().id]) if shows.exists() else '#',
        'show_form_action_url': reverse('add_show'),
        'active_tab': 'episodeFormTab',
        'selected_show': None,
    }
    return render(request, 'dashboard.html', context)

@login_required
def add_show(request):
    shows = Show.objects.prefetch_related('episodes').order_by('order')

    if request.method == 'POST':
        form = ShowForm(request.POST)
        if form.is_valid():
            show = form.save(commit=False)
            show.order = Show.objects.count()
            show.save()
            messages.success(request, f"Show '{show.title}' added successfully!")
            return redirect('dashboard')  # Redirect only on success
        else:
            messages.error(request, "Failed to add show. Please check the form.")

            # Render dashboard with form errors, stay on Show tab
            context = {
                'shows': shows,
                'show_form': form,
                'episode_form': EpisodeForm(),  # Empty episode form
                'edit_mode': False,
                'form_action_url': reverse('add_episode', args=[shows.first().id]) if shows else '#',
                'show_form_action_url': reverse('add_show'),  # Correct action URL
                'active_tab': 'showFormTab',
                'selected_show': None,
            }
            return render(request, 'dashboard.html', context)

    # GET request - just redirect
    return redirect('dashboard')

@login_required
def edit_show(request, pk):
    show = get_object_or_404(Show, pk=pk)
    shows = Show.objects.prefetch_related('episodes').order_by('order')

    if request.method == 'POST':
        form = ShowForm(request.POST, instance=show)
        if form.is_valid():
            form.save()
            messages.success(request, f"Show '{show.title}' updated successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Failed to update show. Please check the form.")
    else:
        form = ShowForm(instance=show)

    context = {
        'shows': shows,
        'episode_form': EpisodeForm(),  # Blank episode form
        'edit_mode': True,
        'form_action_url': reverse('add_episode', args=[shows.first().id]) if shows else '#',
        'show_form': form,
        'show_form_action_url': reverse('edit_show', args=[pk]),
        'active_tab': 'showFormTab',
        'selected_show': None,  # Not editing a specific episode
    }
    return render(request, 'dashboard.html', context)

@login_required
def delete_show(request, pk):
    """Delete a show"""
    show = get_object_or_404(Show, pk=pk)
    title = show.title
    show.delete()

    # Reorder remaining shows efficiently
    shows = Show.objects.order_by('order')
    for i, show in enumerate(shows):
        show.order = i
    Show.objects.bulk_update(shows, ['order'])

    messages.success(request, f"Show '{title}' deleted successfully!")
    return redirect('dashboard')

@login_required
def add_episode(request, show_id):
    show = get_object_or_404(Show, pk=show_id)
    shows = Show.objects.prefetch_related('episodes').order_by('order')

    if request.method == 'POST':
        form = EpisodeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

            messages.success(request, f"Episode added successfully.")

            return redirect('dashboard')  # Redirect to clear POST data and avoid resubmission
        else:
            # If invalid, stay on episode tab
            active_tab = 'episodeFormTab'
    else:
        form = EpisodeForm()
        active_tab = 'episodeFormTab'

    return render(request, 'dashboard.html', {
        'shows': shows,
        'episode_form': form,
        'selected_show': show,
        'edit_mode': False,
        'form_action_url': reverse('add_episode', args=[show.id]),
        'show_form': ShowForm(),
        'active_tab': active_tab,
    })

@login_required
def edit_episode(request, pk):
    episode = get_object_or_404(Episode, pk=pk)
    shows = Show.objects.prefetch_related('episodes').order_by('order')

    if request.method == 'POST':
        form = EpisodeForm(request.POST, request.FILES, instance=episode)
        if form.is_valid():
            form.save()
            messages.success(request, f"Episode '{episode.title}' updated successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Failed to update episode. Please check the form.")
    else:
        form = EpisodeForm(instance=episode)

    return render(request, 'dashboard.html', {
        'shows': shows,
        'episode_form': form,
        'edit_mode': True,
        'form_action_url': reverse('edit_episode', args=[episode.id]),
        'episode': episode,
        'show_form': ShowForm(),  # Blank show form
        'active_tab': 'episodeFormTab',
    })

@login_required
def delete_episode(request, pk):
    """Delete an episode"""
    episode = get_object_or_404(Episode, pk=pk)
    show = episode.show
    title = episode.title
    episode.delete()

    # Reorder remaining episodes
    episodes = show.episodes.order_by('order')
    for i, episode in enumerate(episodes):
        episode.order = i + 1
    Episode.objects.bulk_update(episodes, ['order'])

    messages.success(request, f"Episode '{title}' deleted successfully!")
    return redirect('dashboard')





from django.db.models import F

@login_required
def move_show(request, pk, direction):
    """Move a show up or down in the list"""
    show = get_object_or_404(Show, pk=pk)

    # Convert direction to int
    direction = int(direction)

    # Order shows properly and ensure ordering is consistent
    shows = list(Show.objects.order_by('order'))

    try:
        index = shows.index(show)
        new_index = index + direction

        if 0 <= new_index < len(shows):
            other_show = shows[new_index]
            # Swap order values
            show.order, other_show.order = other_show.order, show.order
            show.save()
            other_show.save()
    except ValueError:
        pass  # Show not found in the list for some reason

    return redirect('dashboard')


@login_required
def move_episode(request, pk, direction):
    """Move an episode up or down in the show"""
    episode = get_object_or_404(Episode, pk=pk)

    # Convert direction to int
    direction = int(direction)

    # Get episodes for this show ordered by 'order'
    episodes = list(episode.show.episodes.order_by('order'))

    try:
        index = episodes.index(episode)
        new_index = index + direction

        if 0 <= new_index < len(episodes):
            other_episode = episodes[new_index]
            # Swap order values
            episode.order, other_episode.order = other_episode.order, episode.order
            episode.save()
            other_episode.save()
    except ValueError:
        pass  # Episode not found in list

    return redirect('dashboard')





@login_required
def settings(request):
    shows = Show.objects.prefetch_related('episodes').order_by('order')
    settings = AppSettings.get_settings()
    settings_form = AppSettingsForm(instance=settings)
    
    return render(request, 'settings.html', {
        'shows': shows,
        'app_settings': settings,
        'settings_form': settings_form,
    })




@login_required
def update_settings(request):
    """Update app settings separately for Roku and Fire TV"""
    settings = AppSettings.get_settings()
    
    if request.method == 'POST':
        form = AppSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, "App settings updated successfully!")
        else:
            messages.error(request, "Failed to update settings. Please check the form.")
    
    return redirect('settings')










from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import AppSettings
from .roku import publish_to_roku
from .views import publish_firetv_feed

@login_required
def publish(request):
    """Publish content to selected platforms"""
    if request.method == 'POST':
        form = PublishForm(request.POST)
        if form.is_valid():
            platform = form.cleaned_data['platform']
            settings = AppSettings.get_settings()
            success_messages = []

            try:
                if platform in ['roku', 'both']:
                    publish_to_roku()
                    settings.last_roku_publish = timezone.now()
                    success_messages.append("✅ Published to Roku successfully!")

                if platform in ['firetv', 'both']:
                    publish_firetv_feed()
                    settings.last_firetv_publish = timezone.now()
                    success_messages.append("✅ Published to Fire TV successfully!")

                settings.save()

                for msg in success_messages:
                    messages.success(request, msg)

            except Exception as e:
                messages.error(request, f"❌ Publishing error: {str(e)}")

    return redirect('dashboard')



