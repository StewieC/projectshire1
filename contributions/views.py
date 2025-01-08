# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Group, PayoutCycle
from .forms import GroupForm, ContributionForm, MemberManagementForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib import messages
import uuid




@login_required
def dashboard(request):
    groups = Group.objects.filter(members=request.user)
    group_form = GroupForm()

    if 'name' in request.POST:  # Group creation
        group_form = GroupForm(request.POST)
        if group_form.is_valid():
            group = group_form.save(commit=False)  # Prevent immediate save
            group.admin = request.user  # Set admin to current user
            group.save()  # Now save the group
            group.members.add(request.user)  # Add creator as member
            messages.success(request, 'Group created successfully.')
            return redirect('dashboard')
        elif 'group_code' in request.POST:  # Joining a group
            group_id = request.POST.get('group_code')
            group = get_object_or_404(Group, id=group_id)
            group.members.add(request.user)
            messages.success(request, 'Successfully joined the group.')
            return redirect('dashboard')

    return render(request, 'contributions/dashboard.html', {
        'groups': groups,
        'group_form': group_form
    })
    
    
@login_required
def contribute(request):
    if request.method == 'POST':
        form = ContributionForm(request.POST)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.member = request.user
            contribution.group = Group.objects.first()  # Assign the first group for simplicity
            contribution.save()
            return redirect('dashboard')
    else:
        form = ContributionForm()

    return render(request, 'contributions/contribute.html', {'form': form})

@login_required
def manage_cycle(request):
    user_groups = Group.objects.filter(members=request.user)
    next_payout = PayoutCycle.objects.filter(group__in=user_groups, status=False).first()
    
    if next_payout and next_payout.recipient == request.user:
        next_payout.status = True
        next_payout.save()
        # Handle payout logic and interest deduction
    
    return redirect('dashboard')

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if request.user not in group.members.all():
        messages.error(request, "You are not authorized to view this group.")
        return redirect('dashboard')

    form = MemberManagementForm()

    if request.method == 'POST':
        if 'generate_code' in request.POST:
            group.generate_join_code()
            messages.success(request, f"Join code generated: {group.join_code}")
        elif 'manage_member' in request.POST:
            form = MemberManagementForm(request.POST)
            if form.is_valid():
                user = form.cleaned_data['user']
                action = form.cleaned_data['action']
                if action == 'add':
                    group.members.add(user)
                    messages.success(request, f"{user.username} added to the group.")
                elif action == 'remove':
                    if user == group.admin:
                        messages.error(request, "Admin cannot be removed from the group.")
                    else:
                        group.members.remove(user)
                        messages.success(request, f"{user.username} removed from the group.")
        return redirect('group_detail', group_id=group.id)

    return render(request, 'contributions/group_detail.html', {
        'group': group,
        'form': form
    })


#   contributions = group.contribution_set.all()
#  'contributions': contributions


@login_required
def join_group(request):
    if request.method == 'POST':
        join_code = request.POST.get('group_code')
        
        try:
            group = Group.objects.get(join_code=join_code)
            if request.user in group.members.all():
                messages.info(request, "You are already a member of this group.")
            else:
                group.members.add(request.user)
                messages.success(request, f"You have successfully joined {group.name}.")
        except Group.DoesNotExist:
            messages.error(request, "Invalid join code. Please try again.")
        
    return redirect('dashboard')

@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.admin = request.user  # Automatically set the user as admin
            group.save()
            group.add_member(request.user)  # Add the creator as a member
            messages.success(request, 'Group created successfully!')
            return redirect('dashboard')
    else:
        form = GroupForm()
    return render(request, 'contributions/create_group.html', {'form': form})

@login_required
def generate_join_code(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.user == group.admin:
        group.join_code = str(uuid.uuid4())[:8]
        group.save()
        messages.success(request, f'Join code generated: {group.join_code}')
    else:
        messages.error(request, 'You are not authorized to generate a join code.')
    return redirect('group_detail', group_id=group.id)
