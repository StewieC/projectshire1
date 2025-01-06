# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Group, PayoutCycle
from .forms import GroupForm, ContributionForm
from django.contrib import messages

@login_required
def dashboard(request):
    groups = Group.objects.filter(members=request.user)
    group_form = GroupForm()

    if request.method == 'POST':
        if 'name' in request.POST:  # Group creation
            group_form = GroupForm(request.POST)
            if group_form.is_valid():
                group = group_form.save()
                group.members.add(request.user)
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

    # Ensure the user is part of the group
    if request.user not in group.members.all():
        messages.error(request, "You are not authorized to view this group.")
        return redirect('dashboard')

    contributions = group.contribution_set.all()

    return render(request, 'contributions/group_detail.html', {
        'group': group,
        'contributions': contributions
    })
